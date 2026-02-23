-- Enable Realtime for game-related tables
ALTER PUBLICATION supabase_realtime ADD TABLE games;
ALTER PUBLICATION supabase_realtime ADD TABLE players;
ALTER PUBLICATION supabase_realtime ADD TABLE messages;
ALTER PUBLICATION supabase_realtime ADD TABLE game_pending;
ALTER PUBLICATION supabase_realtime ADD TABLE hands;
