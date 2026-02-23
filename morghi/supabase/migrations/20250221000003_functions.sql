-- Deck composition per readme: 11 Hen, 11 Rooster, 11 Nest, 7 Fox, 4 Snake, 6 Trap = 46 cards
CREATE OR REPLACE FUNCTION build_deck() RETURNS JSONB AS $$
DECLARE
  deck JSONB := '[]'::jsonb;
  i INT;
BEGIN
  FOR i IN 1..11 LOOP deck := deck || '"Hen"'::jsonb; END LOOP;
  FOR i IN 1..11 LOOP deck := deck || '"Rooster"'::jsonb; END LOOP;
  FOR i IN 1..11 LOOP deck := deck || '"Nest"'::jsonb; END LOOP;
  FOR i IN 1..7 LOOP deck := deck || '"Fox"'::jsonb; END LOOP;
  FOR i IN 1..4 LOOP deck := deck || '"Snake"'::jsonb; END LOOP;
  FOR i IN 1..6 LOOP deck := deck || '"Trap"'::jsonb; END LOOP;
  RETURN deck;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Shuffle jsonb array
CREATE OR REPLACE FUNCTION shuffle_jsonb_array(arr JSONB) RETURNS JSONB AS $$
BEGIN
  RETURN (
    SELECT jsonb_agg(elem ORDER BY random())
    FROM jsonb_array_elements(arr) AS elem
  );
END;
$$ LANGUAGE plpgsql;

-- Start game: min 2 players, all ready, shuffle deck, deal 4 each, set first current_player
CREATE OR REPLACE FUNCTION start_game(p_game_id UUID)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  v_player_count INT;
  v_all_ready BOOLEAN;
  v_deck JSONB;
  v_hand JSONB;
  v_player RECORD;
  v_order INT := 0;
BEGIN
  SELECT COUNT(*), bool_and(ready) INTO v_player_count, v_all_ready
  FROM players WHERE game_id = p_game_id AND left_at IS NULL;

  IF v_player_count < 2 THEN
    RAISE EXCEPTION 'Need at least 2 players to start';
  END IF;
  IF NOT v_all_ready THEN
    RAISE EXCEPTION 'All players must be ready';
  END IF;
  IF (SELECT state FROM games WHERE id = p_game_id) != 'lobby' THEN
    RAISE EXCEPTION 'Game already started';
  END IF;

  -- Build and shuffle deck
  v_deck := shuffle_jsonb_array(build_deck());

  -- Create game_deck row
  INSERT INTO game_deck (game_id, deck, discard)
  VALUES (p_game_id, v_deck, '[]'::jsonb);

  -- Assign player_order (random) and deal 4 cards each
  FOR v_player IN
    SELECT id FROM players WHERE game_id = p_game_id AND left_at IS NULL ORDER BY random()
  LOOP
    UPDATE players SET player_order = v_order WHERE game_id = p_game_id AND id = v_player.id;

    -- Draw 4 cards from deck (first 4 elements)
    v_hand := (
      SELECT jsonb_agg(elem ORDER BY ord)
      FROM (
        SELECT elem, ord FROM jsonb_array_elements(v_deck) WITH ORDINALITY AS t(elem, ord)
        WHERE ord <= 4
      ) sub
    );
    v_deck := (
      SELECT COALESCE(jsonb_agg(elem ORDER BY ord), '[]'::jsonb)
      FROM (
        SELECT elem, ord FROM jsonb_array_elements(v_deck) WITH ORDINALITY AS t(elem, ord)
        WHERE ord > 4
      ) sub
    );

    INSERT INTO hands (game_id, player_id, cards) VALUES (p_game_id, v_player.id, COALESCE(v_hand, '[]'::jsonb));

    v_order := v_order + 1;
  END LOOP;

  -- Update deck (we consumed cards)
  UPDATE game_deck SET deck = v_deck WHERE game_id = p_game_id;

  -- Set game state and current player
  UPDATE games
  SET state = 'playing', current_player_order = 0, updated_at = now()
  WHERE id = p_game_id;

  -- System message
  INSERT INTO messages (game_id, sender_id, message)
  VALUES (p_game_id, NULL, 'Game started!');
END;
$$;

-- Leave game: discard hand, mark player left
CREATE OR REPLACE FUNCTION leave_game(p_game_id UUID)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  v_user_id UUID := auth.uid();
  v_hand JSONB;
  v_discard JSONB;
  v_state game_state;
  v_remaining INT;
BEGIN
  IF v_user_id IS NULL THEN
    RAISE EXCEPTION 'Not authenticated';
  END IF;

  SELECT state INTO v_state FROM games WHERE id = p_game_id;
  IF v_state IS NULL THEN
    RAISE EXCEPTION 'Game not found';
  END IF;

  -- Get hand and move to discard
  SELECT cards INTO v_hand FROM hands WHERE game_id = p_game_id AND player_id = v_user_id;
  IF v_hand IS NOT NULL AND jsonb_array_length(v_hand) > 0 THEN
    SELECT discard INTO v_discard FROM game_deck WHERE game_id = p_game_id;
    v_discard := COALESCE(v_discard, '[]'::jsonb) || v_hand;
    UPDATE game_deck SET discard = v_discard WHERE game_id = p_game_id;
  END IF;

  DELETE FROM hands WHERE game_id = p_game_id AND player_id = v_user_id;
  UPDATE players SET left_at = now() WHERE game_id = p_game_id AND id = v_user_id;

  -- System message
  INSERT INTO messages (game_id, sender_id, message)
  SELECT p_game_id, NULL, p.name || ' left the game'
  FROM players p WHERE p.game_id = p_game_id AND p.id = v_user_id;

  -- If playing, check win condition (only 1 left)
  IF v_state = 'playing' THEN
    SELECT COUNT(*) INTO v_remaining FROM players WHERE game_id = p_game_id AND left_at IS NULL;
    IF v_remaining <= 1 THEN
      UPDATE games SET state = 'finished', updated_at = now() WHERE id = p_game_id;
      INSERT INTO messages (game_id, sender_id, message)
      VALUES (p_game_id, NULL, 'Game over.');
    END IF;
  END IF;
END;
$$;

-- Draw cards from deck (used by action handlers). Returns new hand.
-- Reshuffles discard into deck when deck has < count cards.
CREATE OR REPLACE FUNCTION draw_cards(p_game_id UUID, p_player_id UUID, p_count INT)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  v_deck JSONB;
  v_discard JSONB;
  v_hand JSONB;
  v_drawn JSONB;
  v_remaining JSONB;
BEGIN
  SELECT deck, discard INTO v_deck, v_discard FROM game_deck WHERE game_id = p_game_id;

  -- Reshuffle if needed
  WHILE (SELECT jsonb_array_length(v_deck)) < p_count LOOP
    v_deck := shuffle_jsonb_array(v_discard) || v_deck;
    v_discard := '[]'::jsonb;
    UPDATE game_deck SET deck = v_deck, discard = v_discard WHERE game_id = p_game_id;
  END LOOP;

  -- Draw p_count cards
  v_drawn := (
    SELECT jsonb_agg(elem) FROM (
      SELECT elem FROM jsonb_array_elements(v_deck) WITH ORDINALITY AS t(elem, ord)
      WHERE ord <= p_count
    ) sub
  );
  v_remaining := (
    SELECT COALESCE(jsonb_agg(elem), '[]'::jsonb) FROM (
      SELECT elem FROM jsonb_array_elements(v_deck) WITH ORDINALITY AS t(elem, ord)
      WHERE ord > p_count
    ) sub
  );

  UPDATE game_deck SET deck = v_remaining WHERE game_id = p_game_id;

  -- Append to existing hand
  SELECT cards INTO v_hand FROM hands WHERE game_id = p_game_id AND player_id = p_player_id;
  v_hand := COALESCE(v_hand, '[]'::jsonb) || COALESCE(v_drawn, '[]'::jsonb);
  UPDATE hands SET cards = v_hand WHERE game_id = p_game_id AND player_id = p_player_id;

  RETURN v_hand;
END;
$$;

-- Remove cards from hand (by value, removes first occurrence of each). Returns new hand.
CREATE OR REPLACE FUNCTION remove_cards_from_hand(
  p_game_id UUID, p_player_id UUID, p_cards_to_remove JSONB
) RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  v_new_hand JSONB;
  i INT;
BEGIN
  SELECT cards INTO v_new_hand FROM hands WHERE game_id = p_game_id AND player_id = p_player_id;
  v_new_hand := COALESCE(v_new_hand, '[]'::jsonb);
  FOR i IN 1..COALESCE(jsonb_array_length(p_cards_to_remove), 0) LOOP
    v_new_hand := v_new_hand - jsonb_array_element(p_cards_to_remove, i - 1);
  END LOOP;
  UPDATE hands SET cards = v_new_hand WHERE game_id = p_game_id AND player_id = p_player_id;
  RETURN v_new_hand;
END;
$$;

-- Simple actions: LayEgg, HatchEgg, SkipTurn (complex actions go to Edge Functions)
CREATE OR REPLACE FUNCTION execute_simple_action(
  p_game_id UUID,
  p_action_type TEXT,
  p_cards JSONB,
  p_params JSONB DEFAULT NULL
) RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  v_user_id UUID := auth.uid();
  v_state game_state;
  v_current_order INT;
  v_player_order INT;
  v_next_order INT;
  v_actor_eggs INT;
  v_players_with_eggs INT;
BEGIN
  IF v_user_id IS NULL THEN RAISE EXCEPTION 'Not authenticated'; END IF;

  SELECT state, current_player_order INTO v_state, v_current_order FROM games WHERE id = p_game_id;
  IF v_state IS NULL THEN RAISE EXCEPTION 'Game not found'; END IF;
  IF v_state != 'playing' THEN RAISE EXCEPTION 'Game not in play'; END IF;

  SELECT player_order INTO v_player_order FROM players WHERE game_id = p_game_id AND id = v_user_id AND left_at IS NULL;
  IF v_player_order IS NULL THEN RAISE EXCEPTION 'Not in game'; END IF;
  IF v_player_order != v_current_order THEN RAISE EXCEPTION 'Not your turn'; END IF;

  -- Check no pending action
  IF EXISTS (SELECT 1 FROM game_pending WHERE game_id = p_game_id) THEN
    RAISE EXCEPTION 'Pending action - cannot play';
  END IF;

  CASE p_action_type
    WHEN 'LayEgg' THEN
      IF p_cards @> '["Hen","Rooster","Nest"]'::jsonb AND jsonb_array_length(p_cards) = 3 THEN
        PERFORM remove_cards_from_hand(p_game_id, v_user_id, p_cards);
        UPDATE players SET eggs = eggs + 1 WHERE game_id = p_game_id AND id = v_user_id;
        INSERT INTO messages (game_id, sender_id, message)
        SELECT p_game_id, NULL, p.name || ' laid an egg!' FROM players p WHERE p.game_id = p_game_id AND p.id = v_user_id;
      ELSE
        RAISE EXCEPTION 'Invalid LayEgg: need Hen, Rooster, Nest';
      END IF;

    WHEN 'HatchEgg' THEN
      SELECT eggs INTO v_actor_eggs FROM players WHERE game_id = p_game_id AND id = v_user_id;
      IF v_actor_eggs < 1 THEN RAISE EXCEPTION 'Need at least 1 egg to hatch'; END IF;
      IF p_cards @> '["Hen","Hen"]'::jsonb AND jsonb_array_length(p_cards) = 2 THEN
        PERFORM remove_cards_from_hand(p_game_id, v_user_id, p_cards);
        UPDATE players SET eggs = eggs - 1, chickens = chickens + 1 WHERE game_id = p_game_id AND id = v_user_id;
        INSERT INTO messages (game_id, sender_id, message)
        SELECT p_game_id, NULL, p.name || ' hatched an egg into a chicken!' FROM players p WHERE p.game_id = p_game_id AND p.id = v_user_id;
      ELSE
        RAISE EXCEPTION 'Invalid HatchEgg: need 2 Hens';
      END IF;

    WHEN 'SkipTurn' THEN
      IF jsonb_array_length(p_cards) != 1 THEN RAISE EXCEPTION 'SkipTurn: return exactly 1 card'; END IF;
      PERFORM remove_cards_from_hand(p_game_id, v_user_id, p_cards);
      INSERT INTO messages (game_id, sender_id, message)
      SELECT p_game_id, NULL, p.name || ' skipped their turn' FROM players p WHERE p.game_id = p_game_id AND p.id = v_user_id;

    ELSE
      RAISE EXCEPTION 'Use Edge Function for action: %', p_action_type;
  END CASE;

  -- Draw replacement cards (3 for LayEgg/HatchEgg, 1 for SkipTurn)
  IF p_action_type = 'SkipTurn' THEN
    PERFORM draw_cards(p_game_id, v_user_id, 1);
  ELSE
    PERFORM draw_cards(p_game_id, v_user_id, jsonb_array_length(p_cards));
  END IF;

  -- Advance to next player
  SELECT COALESCE(MIN(player_order), 0) INTO v_next_order
  FROM players WHERE game_id = p_game_id AND left_at IS NULL AND player_order > v_current_order;
  IF v_next_order = 0 THEN
    SELECT COALESCE(MIN(player_order), 0) INTO v_next_order
    FROM players WHERE game_id = p_game_id AND left_at IS NULL;
  END IF;
  UPDATE games SET current_player_order = v_next_order, updated_at = now() WHERE id = p_game_id;
END;
$$;
