import typing as T


class PlayerState(T.TypedDict):
    id: int
    name: str
    ready: bool
    eggs: int
    chickens: int


class YouState(T.TypedDict):
    id: int
    hand: list[str]
    eggs: int
    chickens: int


class GameState(T.TypedDict):
    id: int
    name: str
    status: str
    players: list[PlayerState]
    you: YouState
    chat: list[ChatMessage]


class ChatMessage(T.TypedDict):
    id: str
    sender: str
    text: str
    ts: int
