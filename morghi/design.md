# Overview
An online multiplayer realtime card game.
Tech Stack: Supabase + Bun / Vite / Vue

# Architecture
The project consists of the following modules:
- **Core:** Models and Service Interfaces
- **Resources:** Icons, fonts, binary files, static files, etc
- **App:** All app services, each implementing its related interface.
  - **\[Service\]:** Implementation of each app service. The 'App' module includes many of these.
- **Gui:** The Vue app. Service dependencies are passed down by Provide / Inject, other (usually ui-related) dependencies by prop-drilling.

## Module Dependencies:
**Core:** Nothing
**Resources:** Nothing
**App:** Core, Resources and non-UI external libraries (if required)
  - **\[Service\]:** Implementation of some service interface.
**Gui:** App (recursively), Vue and External UI-related libraries (if required).

## File Structure
The project's file structure reflects the architecture, as described below.
  - **cor:** The **Core** module
  - **app:** The **App** module
    - **\[ServiceImpl\](.ts):** Either a directory with an `index.ts` file or a pure `.ts` file, implementing a specified service interface.
  - **res:** The **Resources** module
  - **gui:** The **Gui** module directory where the UI lives

# User Stories
User stories are separated into multiple stages, each preferably (strongly suggested but not strictly) separated by a gui page.
When the system starts, the root app page decides which page to show based on the state of the app (whether the user is logged in, whether they're in-game right now, etc.)

## Auth Stage:
1. User should be able to sign-up using simple username (or email) and password pair, by verifying their email address.
2. User should be able to sign-in using simple username and password pair.

## User Stage:
1. User should be able to create a game, or join a game created by another user.
2. User can only join one game at a time. If they want to join another game, they should first leave the one they currently joined. (Preferably, the lobby page is skipped if the user in-game and jumped to the game page)

## Game Stage:
1. The game starts after A) There's at least 2 players in the game, and B) All players in the game set their `ready` state to true.
2. All players who have joined a game are allowed to participate in the game's text-based global chat, either before or after the game has started.
3. The game does not allow new players to join the game after the game has started.
4. If a player leaves the game, they'll lose and won't be able to join that same game again.
5. The player should be able to see the playing cards in their hand only. Score cards (eggs and chickens) are visible to everyone.
6. The game is turn-based, the order the players draw cards is random and determined once at the start of the game (remains consistent until the end of the game)
7. The player should be able to draw a combination of cards by selecting them on the UI then pressing the Draw button. The draw button should be active if the card combination matches one of the following (with extra rules if required):
    - Nest + Rooster + Hen: Can always draw. It will result in getting one egg.
    - Hen + Hen: Can draw only if there's at least one egg. It hatches the egg into a chicken.
    - Fox: Can draw if another player has at least 1 egg. Workflow described below.
    - Snake: Can draw if another player has at least 1 egg. Workflow described below.
    - Trap: Can always draw. Workflow described below.
8. When Player X draws Fox: They will choose another player who has at least 1 egg to steal from, let's call them Player Y.
   1. If Y has at least 2 roosters, then they have the option to defend or let the eggs be stolen. The option is shown to them (in realtime, e.g. X is trying to steal your egg) and they'll choose whether to defend the egg by playing the 2 Rooster cards at that moment (outside of their turn).
   2. If Y doesn't have 2 roosters, the egg will be stolen. The option to defend will be disabled for Y, but still shown.
   3. X's turn must wait for Y's response (it won't end until Y responds, or their response times out)
   4. If X steals Y's egg, the egg will be removed from Y and added to X.
9. When Player X draws Snake: They will choose another player who has at least 1 egg to eat from, let's call them Player Y.
   1. If Y has only 1 egg, that egg will be eaten by the snake (removed from Y, NOT added to X)
   2. If Y has more than 1 egg, then X can choose to eat either 1 or 2 eggs.
10. When Player X draws Trap: They will choose another player to target, let's call them Player Y.
   1. X can watch Y's hand.
   2. If Y has at least one Animal card (Hen, Rooster, Snake, Fox), X must choose one of them to kill.
   3. If Y has no animal cards, X can't do anything further.