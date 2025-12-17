from morghi.core import rules, GameState, GameInfo
from .event_announcer import EventAnnouncer
from .morghi_deck import DeckOfCards
from .morghi_player import Player


class Game:
    def __init__(self, id: int, name: str) -> None:
        self.id = id
        self.name = name
        self.announcer = EventAnnouncer()
        self.players: dict[int, Player] = {}
        self.deck = DeckOfCards(available_cards=rules.AVAILABLE_CARDS, shuffle=True)
        self.initiate_turn()  # giving each player a hand
        self.current_turn = 0

    def get_info(self) -> GameInfo:
        return GameInfo(
            id=self.id,
            name=self.name,
            status="Waiting",
            players=len(self.players),
            capacity=4,
        )

    def get_state_for(self, player: int) -> GameState:
        raise NotImplementedError

    def add_player(self, id: int, name: str) -> bool:
        if id in self.players:
            return False
        self.players[id] = Player(id, name)
        return True

    def initiate_turn(self):
        """
        Start a turn by giving each player a hand.
        """
        for player in self.players.values():
            player.complete_hand(self.deck, indices=None)
