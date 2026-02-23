-- Resolve expired pending actions (call at start of game-state operations)
CREATE OR REPLACE FUNCTION resolve_expired_pending(p_game_id UUID)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  v_pending RECORD;
  v_actor_id UUID;
  v_target_id UUID;
  v_target_eggs INT;
  v_actor_eggs INT;
  v_target_hand JSONB;
  v_animal_cards JSONB;
  v_random_card JSONB;
  v_current_order INT;
  v_next_order INT;
  v_roosters_in_hand INT;
BEGIN
  SELECT * INTO v_pending FROM game_pending WHERE game_id = p_game_id AND timeout < now();
  IF v_pending IS NULL THEN RETURN; END IF;

  v_actor_id := (v_pending.action->'actor'->>'id')::uuid;
  v_target_id := (v_pending.action->'params'->'target'->>'id')::uuid;

  IF v_pending.action->>'type' = 'FoxSteal' THEN
    -- Timeout: egg is stolen
    SELECT eggs INTO v_target_eggs FROM players WHERE game_id = p_game_id AND id = v_target_id;
    IF v_target_eggs >= 1 THEN
      UPDATE players SET eggs = eggs - 1 WHERE game_id = p_game_id AND id = v_target_id;
      UPDATE players SET eggs = eggs + 1 WHERE game_id = p_game_id AND id = v_actor_id;
      INSERT INTO messages (game_id, sender_id, message)
      SELECT p_game_id, NULL, 'Timeout! Egg stolen from ' || p.name
      FROM players p WHERE p.game_id = p_game_id AND p.id = v_target_id;
    END IF;
    PERFORM remove_cards_from_hand(p_game_id, v_actor_id, (v_pending.action->'cards')::jsonb);
    PERFORM draw_cards(p_game_id, v_actor_id, 1);
  ELSIF v_pending.action->>'type' = 'TrapKill' THEN
    IF (v_pending.action->'params'->>'finish')::boolean THEN
      NULL;
    ELSE
      -- Timeout: random animal killed
      SELECT cards INTO v_target_hand FROM hands WHERE game_id = p_game_id AND player_id = v_target_id;
      v_animal_cards := (
        SELECT jsonb_agg(elem) FROM jsonb_array_elements(v_target_hand) elem
        WHERE elem IN ('"Hen"'::jsonb, '"Rooster"'::jsonb, '"Fox"'::jsonb, '"Snake"'::jsonb)
      );
      IF v_animal_cards IS NOT NULL AND jsonb_array_length(v_animal_cards) > 0 THEN
        v_random_card := jsonb_array_element(v_animal_cards, floor(random() * jsonb_array_length(v_animal_cards))::int);
        PERFORM remove_cards_from_hand(p_game_id, v_target_id, jsonb_build_array(v_random_card));
      END IF;
    END IF;
    PERFORM remove_cards_from_hand(p_game_id, v_actor_id, (v_pending.action->'cards')::jsonb);
    PERFORM draw_cards(p_game_id, v_actor_id, 1);
  END IF;

  DELETE FROM game_pending WHERE game_id = p_game_id;

  SELECT current_player_order INTO v_current_order FROM games WHERE id = p_game_id;
  SELECT COALESCE(MIN(player_order), 0) INTO v_next_order
  FROM players WHERE game_id = p_game_id AND left_at IS NULL AND player_order > v_current_order;
  IF v_next_order = 0 THEN
    SELECT COALESCE(MIN(player_order), 0) INTO v_next_order
    FROM players WHERE game_id = p_game_id AND left_at IS NULL;
  END IF;
  UPDATE games SET current_player_order = v_next_order, updated_at = now() WHERE id = p_game_id;
END;
$$;

-- Fox steal: actor initiates, creates pending
CREATE OR REPLACE FUNCTION fox_steal(p_game_id UUID, p_cards JSONB, p_target_id UUID)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  v_user_id UUID := auth.uid();
  v_state game_state;
  v_current_order INT;
  v_player_order INT;
  v_target_eggs INT;
  v_roosters_in_hand INT;
  v_actor RECORD;
  v_target RECORD;
BEGIN
  PERFORM resolve_expired_pending(p_game_id);

  IF v_user_id IS NULL THEN RAISE EXCEPTION 'Not authenticated'; END IF;
  SELECT state, current_player_order INTO v_state, v_current_order FROM games WHERE id = p_game_id;
  IF v_state != 'playing' THEN RAISE EXCEPTION 'Game not in play'; END IF;

  SELECT player_order INTO v_player_order FROM players WHERE game_id = p_game_id AND id = v_user_id AND left_at IS NULL;
  IF v_player_order != v_current_order THEN RAISE EXCEPTION 'Not your turn'; END IF;

  IF EXISTS (SELECT 1 FROM game_pending WHERE game_id = p_game_id) THEN
    RAISE EXCEPTION 'Pending action exists';
  END IF;

  IF NOT (p_cards @> '["Fox"]'::jsonb AND jsonb_array_length(p_cards) = 1) THEN
    RAISE EXCEPTION 'Fox steal requires 1 Fox card';
  END IF;

  SELECT eggs INTO v_target_eggs FROM players WHERE game_id = p_game_id AND id = p_target_id AND left_at IS NULL;
  IF v_target_eggs IS NULL OR v_target_eggs < 1 THEN
    RAISE EXCEPTION 'Target must have at least 1 egg';
  END IF;

  SELECT * INTO v_actor FROM players WHERE game_id = p_game_id AND id = v_user_id;
  SELECT * INTO v_target FROM players WHERE game_id = p_game_id AND id = p_target_id;

  PERFORM remove_cards_from_hand(p_game_id, v_user_id, p_cards);

  INSERT INTO game_pending (game_id, action, timeout)
  VALUES (
    p_game_id,
    jsonb_build_object(
      'type', 'FoxSteal',
      'actor', jsonb_build_object('id', v_actor.id, 'name', v_actor.name, 'eggs', v_actor.eggs, 'chickens', v_actor.chickens),
      'cards', p_cards,
      'params', jsonb_build_object('target', jsonb_build_object('id', v_target.id, 'name', v_target.name, 'eggs', v_target.eggs, 'chickens', v_target.chickens))
    ),
    now() + interval '30 seconds'
  );

  INSERT INTO messages (game_id, sender_id, message)
  SELECT p_game_id, NULL, v_actor.name || ' is trying to steal an egg from ' || v_target.name || '!';
END;
$$;

-- Defend fox: target responds with 2 roosters or lets it happen
CREATE OR REPLACE FUNCTION defend_fox(p_game_id UUID, p_defend boolean)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  v_user_id UUID := auth.uid();
  v_pending RECORD;
  v_target_id UUID;
  v_actor_id UUID;
  v_roosters JSONB := '["Rooster","Rooster"]'::jsonb;
  v_current_order INT;
  v_next_order INT;
BEGIN
  IF v_user_id IS NULL THEN RAISE EXCEPTION 'Not authenticated'; END IF;

  SELECT * INTO v_pending FROM game_pending WHERE game_id = p_game_id;
  IF v_pending IS NULL OR (v_pending.action->>'type') != 'FoxSteal' THEN
    RAISE EXCEPTION 'No FoxSteal pending';
  END IF;

  v_target_id := (v_pending.action->'params'->'target'->>'id')::uuid;
  IF v_target_id != v_user_id THEN RAISE EXCEPTION 'Only target can defend'; END IF;

  v_actor_id := (v_pending.action->'actor'->>'id')::uuid;

  IF p_defend THEN
    IF NOT ((SELECT cards FROM hands WHERE game_id = p_game_id AND player_id = v_user_id) @> '["Rooster","Rooster"]'::jsonb) THEN
      RAISE EXCEPTION 'Need 2 Roosters to defend';
    END IF;
    PERFORM remove_cards_from_hand(p_game_id, v_user_id, v_roosters);
    PERFORM draw_cards(p_game_id, v_user_id, 2);
    INSERT INTO messages (game_id, sender_id, message)
    SELECT p_game_id, NULL, (SELECT name FROM players WHERE game_id = p_game_id AND id = v_user_id) || ' defended with 2 Roosters!';
  ELSE
    UPDATE players SET eggs = eggs - 1 WHERE game_id = p_game_id AND id = v_target_id;
    UPDATE players SET eggs = eggs + 1 WHERE game_id = p_game_id AND id = v_actor_id;
    INSERT INTO messages (game_id, sender_id, message)
    SELECT p_game_id, NULL, (SELECT name FROM players WHERE game_id = p_game_id AND id = v_target_id) || ' let the egg be stolen!';
  END IF;

  PERFORM remove_cards_from_hand(p_game_id, v_actor_id, (v_pending.action->'cards')::jsonb);
  PERFORM draw_cards(p_game_id, v_actor_id, 1);

  DELETE FROM game_pending WHERE game_id = p_game_id;

  SELECT current_player_order INTO v_current_order FROM games WHERE id = p_game_id;
  SELECT COALESCE(MIN(player_order), 0) INTO v_next_order
  FROM players WHERE game_id = p_game_id AND left_at IS NULL AND player_order > v_current_order;
  IF v_next_order = 0 THEN
    SELECT COALESCE(MIN(player_order), 0) INTO v_next_order FROM players WHERE game_id = p_game_id AND left_at IS NULL;
  END IF;
  UPDATE games SET current_player_order = v_next_order, updated_at = now() WHERE id = p_game_id;
END;
$$;

-- Snake eat
CREATE OR REPLACE FUNCTION snake_eat(p_game_id UUID, p_cards JSONB, p_target_id UUID, p_egg_count INT)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  v_user_id UUID := auth.uid();
  v_state game_state;
  v_current_order INT;
  v_target_eggs INT;
  v_actor RECORD;
  v_target RECORD;
  v_next_order INT;
BEGIN
  PERFORM resolve_expired_pending(p_game_id);

  IF v_user_id IS NULL THEN RAISE EXCEPTION 'Not authenticated'; END IF;
  SELECT state, current_player_order INTO v_state, v_current_order FROM games WHERE id = p_game_id;
  IF v_state != 'playing' THEN RAISE EXCEPTION 'Game not in play'; END IF;

  IF (SELECT player_order FROM players WHERE game_id = p_game_id AND id = v_user_id AND left_at IS NULL) != v_current_order THEN
    RAISE EXCEPTION 'Not your turn';
  END IF;

  IF EXISTS (SELECT 1 FROM game_pending WHERE game_id = p_game_id) THEN RAISE EXCEPTION 'Pending action'; END IF;

  IF NOT (p_cards @> '["Snake"]'::jsonb AND jsonb_array_length(p_cards) = 1) THEN
    RAISE EXCEPTION 'Snake eat requires 1 Snake card';
  END IF;

  SELECT eggs INTO v_target_eggs FROM players WHERE game_id = p_game_id AND id = p_target_id AND left_at IS NULL;
  IF v_target_eggs IS NULL OR v_target_eggs < 1 THEN RAISE EXCEPTION 'Target must have at least 1 egg'; END IF;

  IF v_target_eggs = 1 AND p_egg_count != 1 THEN RAISE EXCEPTION 'Target has 1 egg, must eat 1'; END IF;
  IF v_target_eggs >= 2 AND (p_egg_count < 1 OR p_egg_count > 2) THEN RAISE EXCEPTION 'Must eat 1 or 2 eggs'; END IF;

  SELECT * INTO v_actor FROM players WHERE game_id = p_game_id AND id = v_user_id;
  SELECT * INTO v_target FROM players WHERE game_id = p_game_id AND id = p_target_id;

  PERFORM remove_cards_from_hand(p_game_id, v_user_id, p_cards);
  UPDATE players SET eggs = eggs - p_egg_count WHERE game_id = p_game_id AND id = p_target_id;
  PERFORM draw_cards(p_game_id, v_user_id, 1);

  INSERT INTO messages (game_id, sender_id, message)
  SELECT p_game_id, NULL, v_actor.name || '''s snake ate ' || p_egg_count || ' egg(s) from ' || v_target.name || '!';

  SELECT COALESCE(MIN(player_order), 0) INTO v_next_order
  FROM players WHERE game_id = p_game_id AND left_at IS NULL AND player_order > v_current_order;
  IF v_next_order = 0 THEN
    SELECT COALESCE(MIN(player_order), 0) INTO v_next_order FROM players WHERE game_id = p_game_id AND left_at IS NULL;
  END IF;
  UPDATE games SET current_player_order = v_next_order, updated_at = now() WHERE id = p_game_id;
END;
$$;

-- Trap kill step 1: init, creates pending with target hand
CREATE OR REPLACE FUNCTION trap_kill_init(p_game_id UUID, p_cards JSONB, p_target_id UUID)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  v_user_id UUID := auth.uid();
  v_state game_state;
  v_current_order INT;
  v_actor RECORD;
  v_target RECORD;
  v_target_hand JSONB;
BEGIN
  PERFORM resolve_expired_pending(p_game_id);

  IF v_user_id IS NULL THEN RAISE EXCEPTION 'Not authenticated'; END IF;
  SELECT state, current_player_order INTO v_state, v_current_order FROM games WHERE id = p_game_id;
  IF v_state != 'playing' THEN RAISE EXCEPTION 'Game not in play'; END IF;

  IF (SELECT player_order FROM players WHERE game_id = p_game_id AND id = v_user_id AND left_at IS NULL) != v_current_order THEN
    RAISE EXCEPTION 'Not your turn';
  END IF;

  IF EXISTS (SELECT 1 FROM game_pending WHERE game_id = p_game_id) THEN RAISE EXCEPTION 'Pending action'; END IF;

  IF NOT (p_cards @> '["Trap"]'::jsonb AND jsonb_array_length(p_cards) = 1) THEN
    RAISE EXCEPTION 'Trap kill requires 1 Trap card';
  END IF;

  SELECT * INTO v_actor FROM players WHERE game_id = p_game_id AND id = v_user_id;
  SELECT * INTO v_target FROM players WHERE game_id = p_game_id AND id = p_target_id AND left_at IS NULL;
  IF v_target IS NULL THEN RAISE EXCEPTION 'Target not found'; END IF;

  SELECT cards INTO v_target_hand FROM hands WHERE game_id = p_game_id AND player_id = p_target_id;

  PERFORM remove_cards_from_hand(p_game_id, v_user_id, p_cards);

  INSERT INTO game_pending (game_id, action, timeout, last_response)
  VALUES (
    p_game_id,
    jsonb_build_object(
      'type', 'TrapKill',
      'actor', jsonb_build_object('id', v_actor.id, 'name', v_actor.name, 'eggs', v_actor.eggs, 'chickens', v_actor.chickens),
      'cards', p_cards,
      'params', jsonb_build_object('target', jsonb_build_object('id', v_target.id, 'name', v_target.name, 'eggs', v_target.eggs, 'chickens', v_target.chickens), 'finish', false, 'card', null)
    ),
    now() + interval '30 seconds',
    jsonb_build_object('type', 'TrapKill', 'isComplete', false, 'isAwaitingActor', true, 'isAwaitingTarget', false, 'params', jsonb_build_object('targetHand', COALESCE(v_target_hand, '[]'::jsonb)))
  );

  INSERT INTO messages (game_id, sender_id, message)
  SELECT p_game_id, NULL, v_actor.name || ' set a trap on ' || v_target.name || '!';
END;
$$;

-- Trap kill step 2: actor selects card to kill (or null to discard)
CREATE OR REPLACE FUNCTION trap_kill_finish(p_game_id UUID, p_card_to_kill TEXT)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  v_user_id UUID := auth.uid();
  v_pending RECORD;
  v_target_id UUID;
  v_actor_id UUID;
  v_current_order INT;
  v_next_order INT;
  v_card_json JSONB;
BEGIN
  IF v_user_id IS NULL THEN RAISE EXCEPTION 'Not authenticated'; END IF;

  SELECT * INTO v_pending FROM game_pending WHERE game_id = p_game_id;
  IF v_pending IS NULL OR (v_pending.action->>'type') != 'TrapKill' THEN
    RAISE EXCEPTION 'No TrapKill pending';
  END IF;

  v_actor_id := (v_pending.action->'actor'->>'id')::uuid;
  IF v_actor_id != v_user_id THEN RAISE EXCEPTION 'Only actor can finish trap'; END IF;

  v_target_id := (v_pending.action->'params'->'target'->>'id')::uuid;

  IF p_card_to_kill IS NOT NULL AND p_card_to_kill != '' THEN
    v_card_json := to_jsonb(p_card_to_kill::text);
    PERFORM remove_cards_from_hand(p_game_id, v_target_id, jsonb_build_array(v_card_json));
  END IF;

  PERFORM draw_cards(p_game_id, v_user_id, 1);

  DELETE FROM game_pending WHERE game_id = p_game_id;

  INSERT INTO messages (game_id, sender_id, message)
  SELECT p_game_id, NULL,
    CASE WHEN p_card_to_kill IS NOT NULL AND p_card_to_kill != ''
      THEN (SELECT name FROM players WHERE game_id = p_game_id AND id = v_user_id) || ' killed a ' || p_card_to_kill || '!'
      ELSE (SELECT name FROM players WHERE game_id = p_game_id AND id = v_user_id) || ' discarded the trap.'
    END;

  SELECT current_player_order INTO v_current_order FROM games WHERE id = p_game_id;
  SELECT COALESCE(MIN(player_order), 0) INTO v_next_order
  FROM players WHERE game_id = p_game_id AND left_at IS NULL AND player_order > v_current_order;
  IF v_next_order = 0 THEN
    SELECT COALESCE(MIN(player_order), 0) INTO v_next_order FROM players WHERE game_id = p_game_id AND left_at IS NULL;
  END IF;
  UPDATE games SET current_player_order = v_next_order, updated_at = now() WHERE id = p_game_id;
END;
$$;
