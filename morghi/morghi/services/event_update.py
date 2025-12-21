import typing as T
from morghi.core import GameState, Message


class EventUpdate:
    event: str
    data: T.Any

    def __init__(self, event: str, data: T.Any):
        self.event = event
        self.data = data

    def to_dict(self):
        return {
            "event": self.event,
            "data": self.data,
        }

    @classmethod
    def message(cls, message: Message):
        return EventUpdate(
            event="message",
            data=message,
        )

    @classmethod
    def state(cls, state: GameState):
        return EventUpdate(
            event="state",
            data=state,
        )

    @classmethod
    def game_start(cls):
        return EventUpdate(
            event="game_start",
            data=None,
        )

    @classmethod
    def turn(cls, player_id: int, player_name: str):
        return EventUpdate(
            event="turn",
            data={"id": player_id, "name": player_name},
        )

    @classmethod
    def hand_changed(cls, player_id: int, hand: list[str]):
        return EventUpdate(
            event="hand_changed",
            data={"player": player_id, "hand": hand},
        )

    @classmethod
    def reaction_expectation(cls, cause: str, acting_player: int, reacting_player: int):
        return EventUpdate(
            event="reaction_expectation",
            data={
                "cause": cause,
                "acting_player": acting_player,
                "reacting_player": reacting_player,
            },
        )

    @classmethod
    def scores_changed(cls, player: int, eggs: int, chickens: int):
        return EventUpdate(
            event="scores_changed",
            data={"player": player, "eggs": eggs, "chickens": chickens},
        )

    @classmethod
    def cards_drawn(
        cls, player: int, cards: list[str], args: dict[str, str | int] | None
    ):
        return EventUpdate(
            event="card_drawn",
            data={"player": player, "cards": cards, "args": args},
        )
