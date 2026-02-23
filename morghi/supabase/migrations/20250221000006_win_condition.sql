-- Check if any player has 3 chickens and end the game
CREATE OR REPLACE FUNCTION check_win_condition(p_game_id UUID)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  v_winner RECORD;
BEGIN
  SELECT id, name INTO v_winner
  FROM players
  WHERE game_id = p_game_id AND left_at IS NULL AND chickens >= 3
  LIMIT 1;

  IF v_winner.id IS NOT NULL THEN
    UPDATE games SET state = 'finished', updated_at = now() WHERE id = p_game_id;
    INSERT INTO messages (game_id, sender_id, message)
    VALUES (p_game_id, NULL, v_winner.name || ' wins with 3 chickens!');
  END IF;
END;
$$;

-- Add win check after HatchEgg
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
BEGIN
  IF v_user_id IS NULL THEN RAISE EXCEPTION 'Not authenticated'; END IF;

  SELECT state, current_player_order INTO v_state, v_current_order FROM games WHERE id = p_game_id;
  IF v_state IS NULL THEN RAISE EXCEPTION 'Game not found'; END IF;
  IF v_state != 'playing' THEN RAISE EXCEPTION 'Game not in play'; END IF;

  SELECT player_order INTO v_player_order FROM players WHERE game_id = p_game_id AND id = v_user_id AND left_at IS NULL;
  IF v_player_order IS NULL THEN RAISE EXCEPTION 'Not in game'; END IF;
  IF v_player_order != v_current_order THEN RAISE EXCEPTION 'Not your turn'; END IF;

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
        PERFORM check_win_condition(p_game_id);
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

  IF (SELECT state FROM games WHERE id = p_game_id) = 'finished' THEN RETURN; END IF;

  IF p_action_type = 'SkipTurn' THEN
    PERFORM draw_cards(p_game_id, v_user_id, 1);
  ELSE
    PERFORM draw_cards(p_game_id, v_user_id, jsonb_array_length(p_cards));
  END IF;

  SELECT COALESCE(MIN(player_order), 0) INTO v_next_order
  FROM players WHERE game_id = p_game_id AND left_at IS NULL AND player_order > v_current_order;
  IF v_next_order = 0 THEN
    SELECT COALESCE(MIN(player_order), 0) INTO v_next_order
    FROM players WHERE game_id = p_game_id AND left_at IS NULL;
  END IF;
  UPDATE games SET current_player_order = v_next_order, updated_at = now() WHERE id = p_game_id;
END;
$$;
