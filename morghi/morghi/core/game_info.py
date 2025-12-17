import typing as T


class GameInfo(T.TypedDict):
    id: int
    name: str
    status: str
    players: int
    capacity: int