import typing as T


class PlayerPublicState(T.TypedDict):
    id: int
    name: str
    ready: bool
    eggs: int
    chickens: int


class PlayerPrivateState(PlayerPublicState):
    hand: list[str]


class Message(T.TypedDict):
    id: int
    sender: str
    text: str
    time_ms: float


class GameState(T.TypedDict):
    id: int
    name: str
    status: str
    players: list[PlayerPublicState]
    messages: list[Message]
    is_started: bool
