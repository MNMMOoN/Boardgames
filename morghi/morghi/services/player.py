import typing as T
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

    def put_cards(self, cards: list[str]):
        self.hand.extend(cards)

    def take_cards(
        self, indices: T.Iterable[int], names: list[str]
    ) -> list[str] | None:
        for i in indices:
            if i < 0 or i >= len(self.hand):
                return None
            c = self.hand[i]
            if c in names:
                names.remove(c)
        if len(names) > 0:
            return None
        return [self.hand.pop(i) for i in sorted(indices, reverse=True)]
