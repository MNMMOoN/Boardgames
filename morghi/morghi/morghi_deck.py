from .constants import *
from .morghi_morgh import Morgh
from .morghi_khoros import Khoros
from .morghi_robah import Robah
from .morghi_mar import Mar
from .morghi_loune import Loune
from .morghi_tale import Tale

import random

class DeckOfCards:
    def __init__(self, 
                 available_cards=AVAILABLE_CARDS, available_num_cards=AVAILABLE_NUM_CARDS, 
                 shuffle=True):
        """
        Initialize the deck with available cards and their quantities.
        Parameters:
            available_cards (list)      – list of card classes available in the game
            available_num_cards (list)  – list of integers representing the number of each card class
            shuffle (bool)              – whether to shuffle the deck upon creation
        """
        self.cards = self.create_deck(available_cards= available_cards, available_num_cards=available_num_cards)
        self.available_card_types = available_cards.copy()
        self.available_card_types_num = available_num_cards.copy()

        self.not_in_deck_cards = []
        self.num_not_in_deck_cards = 0

        self.in_deck_cards = self.cards.copy()
        self.num_in_deck_cards = len(self.in_deck_cards)

        self.removed_cards = []
        self.num_removed_cards = 0

        self.shuffle = shuffle
        if self.shuffle:
            self.shuffle_deck()

    def create_deck(self, available_cards, available_num_cards):
        from itertools import chain, repeat
        return list(chain.from_iterable(map(repeat, available_cards, available_num_cards)))

    def shuffle_deck(self):
        random.shuffle(self.cards)

    def _shuffle_played_cards(self):
        random.shuffle(self.not_in_deck_cards)

    def make_deck_complete(self):
        if self.shuffle:
            self._shuffle_played_cards(self)
        self.cards = self.in_deck_cards + self.not_in_deck_cards
        self.not_in_deck_cards = []
        self.in_deck_cards = self.cards.copy()
    
    def give_cards(self, n):
        given = []
        if self.num_in_deck_cards < n:
                self.make_deck_complete()
        for _ in range(n):
            card = self.cards.pop(0)
            given.append(card)
            self.in_deck_cards.remove(card)
            self.num_in_deck_cards -= 1
            self.not_in_deck_cards.append(card)
            self.num_not_in_deck_cards += 1
        return given
    
    def remove_cards(self, kind, n, mode="first"):
        """
        mode:
            - "first"  -> remove first n matching cards
            - "last"   -> remove last n matching cards
            - "random" -> remove n random matching cards
        """

        # Collect matching indices
        indices = [i for i, card in enumerate(self.cards) if card.kind == kind]

        if not indices:
            return []

        n = min(n, len(indices))
        removed = []

        if mode == "first":
            remove_indices = indices[:n]

        elif mode == "last":
            remove_indices = indices[-n:]

        elif mode == "random":
            remove_indices = random.sample(indices, n)

        else:
            raise ValueError("mode must be 'first', 'last', or 'random'")

        # Remove safely from back to front
        for i in sorted(remove_indices, reverse=True):
            card = self.cards.pop(i)
            card.playable = False
            self.removed_cards.append(card)
            self.num_removed_cards += 1
            removed.append(card)

        return removed
    
    def add_cards(self, card_class, n, mode="random"):
        """
        mode:
            - "first"  -> add n cards of the specified kind to the top of the deck
            - "last"   -> add n cards of the specified kind to the bottom of the deck
            - "random" -> add n cards of the specified kind to random positions in the deck
        """

        added = []
        for _ in range(n):
            card = card_class()
            card.playable = True
            card.times_played = 0

            if mode == "first":
                self.in_deck_cards.insert(0, card)

            elif mode == "last":
                self.in_deck_cards.append(card)

            elif mode == "random":
                position = random.randint(0, len(self.cards))
                self.in_deck_cards.insert(position, card)

            else:
                raise ValueError("mode must be 'first', 'last', or 'random'")

            self.cards.append(card)
            self.num_in_deck_cards += 1
            added.append(card)

        if card_class in self.available_card_types:
            index = self.available_card_types.index(card_class)
            self.available_card_types_num[index] += n
        else:
            self.available_card_types.append(card_class)
            self.available_card_types_num.append(n)
        return added
