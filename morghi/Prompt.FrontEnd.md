Implement an mobile-first SPA front-end for a boardgame with the following main views:
- login       : Home-page where the player enters their name, and it displays available games, or an option to create a new game.
- games       : The page after login, where the player can either create a new game or join an existing one.
- game        : The lobby and the main page of the game. Once player joins a game, this page will display the lobby before the game starts, and after the game starts it shows the game interface.
The view `/game` has a live-chat, and all game events (including chat messages) are published to each player through an SSE (Server-Sent Event) channel.
Based on `morghi/services/morghi_server.py`, You're gonna write the following files:
- `morghi/static/main.html` : The app's main html
- `morghi/static/main.css`  : The styles used for all pages
- `morghi/static/main.js`   : The scripts used by all pages

The game page flows as follows:
- There are 6 types of cards available for the Hand and the Deck: Hen (Morgh), Rooster (Khoros), Fox (Robah), Snake (Mar), Nest (Loune), Trap (Tale). Card images and icons will be available as static resources later.
- There are 2 types of scores: Eggs (Tokhm), Chickens (Joojoo). Scores are visible to all players.
- Each player always has exactly 4 cards in their hand, and they're displayed in front of them. Players' hands are not visible to other players.
- Each player can execute one of the following actions in their turn. Each action will be sent to the server as a `draw_cards` request and the logic is handled on server-side. The results are delivered through the SSE channel.
  - If they have at least 1 Hen, 1 Rooster and 1 Nest, They can Lay an Egg.
  - If they have at least 1 Egg and 2 Hens, They can Hatch an Egg to get a Chicken.
  - If they have at least 1 Fox and another player has at least 1 Egg, they can choose to Steal their egg. If the other player has 2 Roosters, they'll be able to defend the egg if they want.
  - If they have at least 1 Snake and another player has at least 1 Egg, they can choose to Break 1 or 2 of their eggs. (Snake can't be defended)
  - If they have at least 1 Trap card, they can choose to see another player's hand and if the other player has any Animal cards, they can choose to kill that animal. If the other player doesn't have an animal, they've only seen the other player's hand.
- If none of the above actions can take place in a player's turn, they must choose one of their cards to be replaced from another in the deck.
- Each player's visible actions are displayed in chat as system messages.