-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Custom types
CREATE TYPE game_state AS ENUM ('lobby', 'playing', 'finished');
CREATE TYPE card_type AS ENUM ('Hen', 'Rooster', 'Nest', 'Fox', 'Snake', 'Trap');

-- Games table
CREATE TABLE games (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  state game_state NOT NULL DEFAULT 'lobby',
  current_player_order INT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Players table (id = auth.uid, links to auth.users)
CREATE TABLE players (
  id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  game_id UUID NOT NULL REFERENCES games(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  eggs INT NOT NULL DEFAULT 0,
  chickens INT NOT NULL DEFAULT 0,
  ready BOOLEAN NOT NULL DEFAULT false,
  player_order INT,
  left_at TIMESTAMPTZ,
  joined_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (id, game_id)
);

-- Messages (chat + system)
CREATE TABLE messages (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  game_id UUID NOT NULL REFERENCES games(id) ON DELETE CASCADE,
  sender_id UUID REFERENCES auth.users(id),
  message TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Game pending (1:1 with game when there's a pending action)
CREATE TABLE game_pending (
  game_id UUID PRIMARY KEY REFERENCES games(id) ON DELETE CASCADE,
  action JSONB NOT NULL,
  timeout TIMESTAMPTZ NOT NULL,
  last_response JSONB
);

-- Game state: deck and discard (cards as jsonb arrays of card_type strings)
CREATE TABLE game_deck (
  game_id UUID PRIMARY KEY REFERENCES games(id) ON DELETE CASCADE,
  deck JSONB NOT NULL DEFAULT '[]'::jsonb,
  discard JSONB NOT NULL DEFAULT '[]'::jsonb
);

-- Hands (backend-managed, RLS restricts to own hand except during Trap)
CREATE TABLE hands (
  game_id UUID NOT NULL REFERENCES games(id) ON DELETE CASCADE,
  player_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  cards JSONB NOT NULL DEFAULT '[]'::jsonb,
  PRIMARY KEY (game_id, player_id)
);

-- Indexes
CREATE INDEX idx_players_game ON players(game_id);
CREATE INDEX idx_messages_game ON messages(game_id);
CREATE INDEX idx_games_state ON games(state);
