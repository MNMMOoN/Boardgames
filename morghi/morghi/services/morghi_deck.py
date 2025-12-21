from morghi.core import rules
import random


class DeckOfCards:
    def __init__(self):
        # a.k.a. in_deck_cards
        self._in_deck_: list[str] = [
            name
            for cards_category in rules.AVAILABLE_CARDS.values()
            for name, count in cards_category.items()
            for _ in range(count)
        ]
        # a.k.a. not_in_deck_cards
        self._reserved_: list[str] = []
        # For now, always Shuffle to keep things simple
        # We can always make it optional if need be
        self.shuffle_deck()

    def take(self, count: int) -> list[str]:
        """
        Takes cards from the top of the deck
        Args:
            count (int): Number of cards to take
        Returns:
            list[str]: List of cards
        """
        given = []
        if len(self._in_deck_) < count:
            self._refill_deck_()
            if len(self._in_deck_) < count:
                raise ValueError(
                    f"Not enough cards; Expected >= {count}, Found = {len(self._in_deck_)}"
                )
        for _ in range(count):
            card = self._in_deck_.pop(0)
            self._reserved_.append(card)
            given.append(card)
        return given

    def put(self, cards: list[str]):
        """
        Put cards back into the deck's reserve
        """
        self._reserved_.extend(cards)

    def shuffle_deck(self):
        """
        Shuffles the deck (but not the reserve)
        """
        random.shuffle(self._in_deck_)

    def shuffle_reserve(self):
        """
        Shuffles the reserved cards
        """
        random.shuffle(self._in_deck_)

    # a.k.a. make_deck_complete
    def _refill_deck_(self):
        """
        Shuffling then moves the reserve to the end of the deck
        """
        self.shuffle_reserve()
        self._in_deck_.extend(self._reserved_)
        self._reserved_.clear()

    # def remove_cards(self, name, n, mode="first"):
    #     """
    #     mode:
    #         - "first"  -> remove first n matching cards
    #         - "last"   -> remove last n matching cards
    #         - "random" -> remove n random matching cards
    #     """
    #     if sum(1 for card in self._in_deck_ if card == name) < n:
    #         self._refill_deck_()
    #         if sum(1 for card in self._in_deck_ if card == name) < n:
    #             n = sum(1 for card in self._in_deck_ if card == name)
    #     # Collect matching indices
    #     indices = [i for i, card in enumerate(self._in_deck_) if card == name]
    #     if not indices:
    #         return []
    #     n = min(n, len(indices))
    #     removed = []
    #     if mode == "first":
    #         remove_indices = indices[:n]
    #     elif mode == "last":
    #         remove_indices = indices[-n:]
    #     elif mode == "random":
    #         remove_indices = random.sample(indices, n)
    #     else:
    #         raise ValueError("mode must be 'first', 'last', or 'random'")
    #     for i in sorted(remove_indices, reverse=True):
    #         card = self._in_deck_.pop(i)
    #         # By simply not adding them to `not_in_deck_cards`, they'll be removed from the game entirely
    #         removed.append(card)
    #     return removed

    # def add_cards(self, card_class, n, mode="random"):
    #     """
    #     mode:
    #         - "first"  -> add n cards of the specified kind to the top of the deck
    #         - "last"   -> add n cards of the specified kind to the bottom of the deck
    #         - "random" -> add n cards of the specified kind to random positions in the deck
    #     """

    #     added = []
    #     for _ in range(n):
    #         card = card_class()
    #         card.playable = True
    #         card.times_played = 0

    #         if mode == "first":
    #             self._in_deck_.insert(0, card)

    #         elif mode == "last":
    #             self._in_deck_.append(card)

    #         elif mode == "random":
    #             position = random.randint(0, len(self._in_deck_))
    #             self._in_deck_.insert(position, card)

    #         else:
    #             raise ValueError("mode must be 'first', 'last', or 'random'")

    #         self._in_deck_.append(card)
    #         added.append(card)

    #     # # TODO: FIX Bugs =>
    #     # if card_class in self.available_card:
    #     #     index = self.available_card.index(card_class)
    #     # else:
    #     #     self.available_card_types_num[index] += n
    #     #     self.available_card.append(card_class)
    #     #     self.available_card_types_num.append(n)
    #     return added
