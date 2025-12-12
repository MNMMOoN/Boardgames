Implement an mobile-first SPA front-end using tailwind for a boardgame with the following pages (i.e. SPA App States):
- login       : Home-page where the player enters their name, and it displays available games, or an option to create a new game.
- game_select : The page after login, where the player can either create a new game or join an existing one.
- lobby       : The lobby page where players set their ready status and wait until the game starts.
- game        : The main page of the game, where the players play once the game starts. The game itself will be explained in details below.
Both `/game` and `/lobby` share a live-chat, and all game events are published to each player through an SSE (Server-Sent Event) channel.
You're gonna write the following files:
- `morghi/flask_app.py`          : A mock Flask app (encapsulate in a class) with the required end-points to serve the gui without errors, the actual functionality will be added later.
- `morghi/static/main.html` : The app's main html
- `morghi/static/main.css`  : The styles used for all pages
- `morghi/static/main.js`   : The scripts used by all pages

The game page's flow is as follows:
- There are 6 types of cards available for the Hand and the Deck: Hen, Rooster, Fox, Snake, Nest, Trap. Card images and icons will be available as static resources.
- There are 2 types of scores: Eggs, Chickens. Scores are visible to all players.
- Each player always has exactly 4 cards in their hand, and they're displayed in front of them. Players' hands are not visible to other players.
- Each player can execute one of the following actions in their turn. Each action will be sent to the server as a request and the logic is handled on server-side. The results are delivered through the SSE channel.
  - If they have at least 1 Hen, 1 Rooster and 1 Nest, They can Lay an Egg.
  - If they have at least 1 Egg and 2 Hens, They can Hatch an Egg to get a Chicken.
  - If they have at least 1 Fox and another player has at least 1 Egg, they can choose to Steal their egg. If the other player has 2 Roosters, they'll be able to defend the egg if they want.
  - If they have at least 1 Snake and another player has at least 1 Egg, they can choose to Break 1 or 2 of their eggs. (Snake can't be defended)
  - If they have at least 1 Trap card, they can choose to see another player's hand and if the other player has any Animal cards, they can choose to kill that animal. If the other player doesn't have an animal, they've only seen the other player's hand.
- If none of the above actions can take place in a player's turn, they must choose one of their cards to be replaced from another in the deck.
- Each player's visible actions are displayed in chat as system messages.

Given the game rules described above ->
- These are the suggested end-points for player actions.
  - GET  `/`                : Serves `main.html`
  - GET  `/main.css`        : Serves `main.css`
  - GET  `/main.js`         : Serves `main.js`
  - POST `/login`           : Sign-in the player with their selected name. No authentication is required yet, just the player name. Logout is handled on client-side only, by removing the authentication token.
  - GET  `/games`           : Used to list the games avaialble in the lobby, and whether they have available space to join.
  - POST `/games`           : Used to create a new game in lobby.
  - GET  `/game/{id}`       : Get the game info to display in the lobby, including its latest state.
  - ???? `/game/{id}/listen`: The endpoint to listen to a game's events. Each player's events are pushed separately (depending on their authentication token). The first returned object is the full game state. Use the correct http method used in SSE instead of ????.
  - POST `/game/{id}/ready` : Send a boolean to indicate whether the player is ready to join the game with game Id = `id`.
- After selecting a game (entering `lobby`), an SSE channel is opened. Once it's opened, the latest game state is received. Afterwards, the following events will be transmitted through the SSE channel. Most are only sent on `game`, the first two as described:
  - SSE `game_started`: Only on `lobby`, Received once all players are `Ready` to join the game, and game `status` is updated to `Playing` and `game` page should be displayed now.
  - SSE `message`: On both `lobby` and `game`, Received a message to update the chat. It includes player-sent or system messages. Define the data structure as you see fit.
  - SSE `hand_changed`: Received once the player's hand is changed. All cards in the hand are re-sent to player.
  - SSE `scores_changed`: Received once any player's scores (eggs or chickens) are changed.
  - SSE `fox_incoming`: Received when another player chose to use a Fox on the player and the player has at least 2 Roosters. The player can now choose to whether defend or let the egg be taken.