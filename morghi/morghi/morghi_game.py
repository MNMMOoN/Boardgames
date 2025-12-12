from .morghi_player import Player
from .morghi_deck import DeckOfCards
from rules import *
from .constants import *
class Game:
    def __init__(self, player_numbers):
        self.players = []
        self._initiate_players(player_numbers)
        self.deck = None
        self._initiate_deck()
        self.initiate_turn() #giving each player a hand
        self.current_turn = 0
        

    def _initiate_deck(self):
        self.deck = DeckOfCards(
            available_cards=AVAILABLE_CARDS, 
            shuffle=True
            )

    def _initiate_players(self, player_numbers):
        for i in range(player_numbers):
            player = Player(name=f"Player {i+1}")
            self.players.append(player)

    def initiate_turn(self):
        """
        start a turn by giving each player a hand.
        """
        for player in self.players:
            player.complete_hand(self.deck, indices=None)

    def play(self):
        # Example of how to use the rules
        tokhm_bedozed(self.player1, self.player2, 1, self.deck)
        tokhm_beshkan(self.player1, self.player2, 1, self.deck)