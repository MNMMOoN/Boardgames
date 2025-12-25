import json
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

    def to_event_text(self):
        return f"event: {self.event}\ndata: {json.dumps(self.data)}\n\n"

    @staticmethod
    def state(state: GameState):
        return EventUpdate(
            event="state",
            data=state,
        )

    @staticmethod
    def message(message: Message):
        return EventUpdate(
            event="message",
            data=message,
        )

    @staticmethod
    def player_ready(player_id: int):
        return EventUpdate(
            event="player_ready",
            data=player_id,
        )

    @staticmethod
    def game_start():
        return EventUpdate(
            event="game_start",
            data=None,
        )

    @staticmethod
    def turn(player_id: int, player_name: str):
        return EventUpdate(
            event="turn",
            data={"id": player_id, "name": player_name},
        )

    @staticmethod
    def hand_changed(player_id: int, hand: list[str]):
        return EventUpdate(
            event="hand_changed",
            data={"player": player_id, "hand": hand},
        )

    @staticmethod
    def scores_changed(player: int, eggs: int, chickens: int):
        return EventUpdate(
            event="scores_changed",
            data={"player": player, "eggs": eggs, "chickens": chickens},
        )
