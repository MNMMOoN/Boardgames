import typing as T


class MorghiConfig(T.TypedDict):
    port: int
    jwt_secret: str
