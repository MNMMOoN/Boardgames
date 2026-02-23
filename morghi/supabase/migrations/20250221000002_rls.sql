-- Enable RLS on all tables
ALTER TABLE games ENABLE ROW LEVEL SECURITY;
ALTER TABLE players ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE game_pending ENABLE ROW LEVEL SECURITY;
ALTER TABLE game_deck ENABLE ROW LEVEL SECURITY;
ALTER TABLE hands ENABLE ROW LEVEL SECURITY;

-- Games: anyone can read lobby games; players can read their game
CREATE POLICY games_select_lobby ON games
  FOR SELECT USING (state = 'lobby');

CREATE POLICY games_select_player ON games
  FOR SELECT USING (
    EXISTS (SELECT 1 FROM players p WHERE p.game_id = games.id AND p.id = auth.uid() AND p.left_at IS NULL)
  );

CREATE POLICY games_insert ON games
  FOR INSERT WITH CHECK (true);

CREATE POLICY games_update_player ON games
  FOR UPDATE USING (
    EXISTS (SELECT 1 FROM players p WHERE p.game_id = games.id AND p.id = auth.uid())
  );

-- Players: players in same game can see each other
CREATE POLICY players_select_same_game ON players
  FOR SELECT USING (
    EXISTS (SELECT 1 FROM players p WHERE p.game_id = players.game_id AND p.id = auth.uid())
  );

CREATE POLICY players_insert ON players
  FOR INSERT WITH CHECK (auth.uid() = id);

CREATE POLICY players_update_self ON players
  FOR UPDATE USING (auth.uid() = id);

-- Messages: players in game can read/write
CREATE POLICY messages_select ON messages
  FOR SELECT USING (
    EXISTS (SELECT 1 FROM players p WHERE p.game_id = messages.game_id AND p.id = auth.uid())
  );

CREATE POLICY messages_insert ON messages
  FOR INSERT WITH CHECK (
    EXISTS (SELECT 1 FROM players p WHERE p.game_id = messages.game_id AND p.id = auth.uid() AND p.left_at IS NULL)
  );

-- Game pending: actor and target can read; backend handles write via service role
CREATE POLICY game_pending_select ON game_pending
  FOR SELECT USING (
    EXISTS (SELECT 1 FROM players p WHERE p.game_id = game_pending.game_id AND p.id = auth.uid())
  );

-- Game deck: only backend (service role) writes; players in game can read for display (deck count hidden, discard count ok)
CREATE POLICY game_deck_select ON game_deck
  FOR SELECT USING (
    EXISTS (SELECT 1 FROM players p WHERE p.game_id = game_deck.game_id AND p.id = auth.uid())
  );

-- Hands: players see only their own hand (Trap flow handled via RPC that returns target hand to actor)
CREATE POLICY hands_select_own ON hands
  FOR SELECT USING (auth.uid() = player_id);
