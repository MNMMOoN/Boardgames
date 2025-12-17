from morghi.core import rules
from .morghi_deck import DeckOfCards


class Player:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name
        # List to hold the player's cards
        self.hand = []
        # Number of cards the player have
        self.num_cards_in_hand = 0
        # Minimum number of cards the player must have
        self.min_cards_in_hand = rules.MIN_NUM_OF_CARDS_IN_HAND
        # Maximum number of cards the player can have
        self.max_cards_in_hand = rules.MAX_NUM_OF_CARDS_IN_HAND

        self.allcards = []  # List to hold all cards the player has been played

        self.active = True  # Player is active in the game
        self.is_turn = False  # Flag to indicate if it's the player's turn
        self.has_played = False  # Flag to indicate if the player has played this turn
        self.played_cards = []  # List to hold actions taken by the player
        self.is_winner = False  # Flag to indicate if the player has won

        self.achievements = []  # List to hold player's achievements
        self.num_of_tokhms = 0
        self.num_of_jojos = 0

    def complete_hand(self, deck, indices):
        if self.num_cards_in_hand < self.min_cards_in_hand:
            n = abs(self.num_cards_in_hand - self.min_cards_in_hand)
            cards = deck.take_cards(n)
            self.hand = self.hand + cards
            self.num_cards_in_hand += n

        if self.num_cards_in_hand > self.max_cards_in_hand:
            n = abs(self.max_cards_in_hand - self.num_cards_in_hand)
            if indices is None or len(indices) == 0:
                indices = range(n)
            for i in indices:
                card = self.hand.pop(i)
                deck.put_cards([card])
                self.num_cards_in_hand -= 1

    def give_cards(self, n, deck, indices=None):
        cards = []

        if n > self.num_cards_in_hand:
            n = self.num_cards_in_hand

        if indices is None:
            indices = range(n)

        for i in indices:
            card = self.hand.pop(i)
            cards.append(card)
            self.num_cards_in_hand -= 1

        if self.num_cards_in_hand < self.min_cards_in_hand:
            self.complete_hand(deck, indices)

    def take_cards(self, n, indices=None, from_=None):
        """
        take cards from the self.hand in specific indeces or randomly to other player or to deck
        """
        if isinstance(from_, DeckOfCards):
            self._take_card_from_deck(from_, n)
        if isinstance(from_, Player):
            self._take_cards_from_player(from_, n, indices)

    def _take_card_from_deck(self, deck, n):
        if n > abs(self.max_cards_in_hand - self.num_cards_in_hand):
            n = abs(self.max_cards_in_hand - self.num_cards_in_hand)

        cards = deck.take_cards(n)
        self.hand = self.hand + cards
        self.num_cards_in_hand += n
        self.is_turn = False

    def _take_cards_from_player(self, player, n, indices):
        if n > self.max_cards_in_hand - self.num_cards_in_hand:
            n = self.max_cards_in_hand - self.num_cards_in_hand

        cards = player.give_card(player, n, indices)
        self.hand = self.hand + cards
        self.num_cards_in_hand += n
        self.is_turn = False

    # def add_cards(self, source, n=None, mode="deck", indices=None, deck=None):
    #     """
    #     Unified card drawing method.

    #     Parameters:
    #         source:
    #             - deck object (when mode="deck")
    #             - player object (when mode="player")
    #         n (int or None):
    #             - number of cards to draw
    #         mode (str):
    #             - "deck"     -> draw from a deck (top cards)
    #             - "player"   -> draw from another player's hand (random by default)
    #         indices (list or None):
    #             - specific indices to draw (only works in mode="player")
    #         deck:
    #             - deck object (used to refill other player's hand if needed)
    #     """

    #     capacity = self.max_cards_in_hand - self.num_cards_in_hand
    #     if capacity <= 0:
    #         return []

    #     if n is None:
    #         n = capacity
    #     else:
    #         n = min(n, capacity)

    #     drawn_cards = []

    #     # ----- DRAW FROM DECK -----
    #     if mode == "deck":
    #         drawn_cards = source.give_cards(n)

    #     # ----- DRAW FROM ANOTHER PLAYER -----
    #     elif mode == "player":
    #         other = source

    #         if other.num_cards_in_hand == 0:
    #             print(f"{other.name} has no cards to draw.")
    #             return []

    #         n = min(n, other.num_cards_in_hand)

    #         # Specific index-based drawing
    #         if indices is not None:
    #             valid_indices = sorted(set(i for i in indices if 0 <= i < len(other.hand)))
    #             valid_indices = valid_indices[:n]

    #         # Random drawing if no indices
    #         else:
    #             valid_indices = random.sample(range(len(other.hand)), n)

    #         # Remove safely from back to front
    #         for i in sorted(valid_indices, reverse=True):
    #             card = other.hand.pop(i)
    #             other.num_cards_in_hand -= 1

    #             # Auto-refill logic
    #             if deck and other.num_cards_in_hand < other.min_cards_in_hand:
    #                 other.draw_cards(deck, mode="deck",
    #                                 n=other.min_cards_in_hand - other.num_cards_in_hand)

    #             self.hand.append(card)
    #             self.num_cards_in_hand += 1
    #             drawn_cards.append(card)

    #     else:
    #         raise ValueError("mode must be 'deck' or 'player'")

    #     # Update hand count
    #     self.hand.extend(drawn_cards) if mode == "deck" else None
    #     self.num_cards_in_hand = len(self.hand)

    #     return drawn_cards
