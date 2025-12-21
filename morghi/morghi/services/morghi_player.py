from morghi.core import PlayerPublicState, PlayerPrivateState


class Player:
    def __init__(self, id: int, name: str):
        self.id: int = id
        self.name: str = name
        self.hand: list[str] = []
        self.drawn_cards: list[str] = []
        self.num_of_tokhms: int = 0
        self.num_of_jojos: int = 0

    def get_state(self, is_ready: bool) -> PlayerPublicState:
        return PlayerPublicState(
            id=self.id,
            name=self.name,
            ready=is_ready,
            eggs=self.num_of_tokhms,
            chickens=self.num_of_jojos,
        )

    def get_private_state(self, is_ready: bool) -> PlayerPrivateState:
        return PlayerPrivateState(
            id=self.id,
            name=self.name,
            ready=is_ready,
            eggs=self.num_of_tokhms,
            chickens=self.num_of_jojos,
            hand=self.hand,
        )

    # def complete_hand(self, deck: DeckOfCards, indices: T.Sequence[int] | None = None):
    #     if len(self.hand) < rules.MIN_NUM_OF_CARDS_IN_HAND:
    #         num_cards_to_add = abs(len(self.hand) - rules.MIN_NUM_OF_CARDS_IN_HAND)
    #         self.hand.extend(deck.take_cards(num_cards_to_add))

    #     if len(self.hand) > rules.MAX_NUM_OF_CARDS_IN_HAND:
    #         num_cards_to_remove = abs(rules.MAX_NUM_OF_CARDS_IN_HAND - len(self.hand))
    #         if indices is None or len(indices) == 0:
    #             indices = range(num_cards_to_remove)
    #         removed_cards = [self.hand.pop(i) for i in sorted(indices, reverse=True)]
    #         deck.put_cards(removed_cards)
    # def give_cards(
    #     self, count: int, deck: DeckOfCards, indices: T.Sequence[int] | None = None
    # ):
    #     cards = []
    #     if count > len(self.hand):
    #         count = len(self.hand)
    #     if indices is None:
    #         indices = range(count)
    #     for i in sorted(indices, reverse=True):
    #         card = self.hand.pop(i)
    #         cards.append(card)
    #     if len(self.hand) < rules.MIN_NUM_OF_CARDS_IN_HAND:
    #         self.complete_hand(deck, indices)
    # def take_cards(
    #     self,
    #     n: int,
    #     indices: T.Sequence[int] | None = None,
    #     from_: Player | DeckOfCards | None = None,
    # ):
    #     if isinstance(from_, DeckOfCards):
    #         self._take_card_from_deck(from_, n)
    #     if isinstance(from_, Player):
    #         self._take_cards_from_player(from_, n, indices)
    # def _take_card_from_deck(self, deck: DeckOfCards, n: int):
    #     if n > abs(self.max_cards_in_hand - len(self.hand)):
    #         n = abs(self.max_cards_in_hand - len(self.hand))
    #     cards = deck.take_cards(n)
    #     self.hand = self.hand + cards
    #     len(self.hand) += n
    # def _take_cards_from_player(
    #     self, player: Player, n: int, indices: T.Sequence[int] | None
    # ):
    #     if n > self.max_cards_in_hand - len(self.hand):
    #         n = self.max_cards_in_hand - len(self.hand)

    #     cards = player.give_card(player, n, indices)  # WTF ?
    #     self.hand = self.hand + cards
    #     len(self.hand) += n
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

    #     capacity = self.max_cards_in_hand - len(self.hand)
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
    #             len(self.hand) += 1
    #             drawn_cards.append(card)

    #     else:
    #         raise ValueError("mode must be 'deck' or 'player'")

    #     # Update hand count
    #     self.hand.extend(drawn_cards) if mode == "deck" else None
    #     len(self.hand) = len(self.hand)

    #     return drawn_cards
