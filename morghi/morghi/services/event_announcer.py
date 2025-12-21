import queue
from .event_update import EventUpdate


class EventAnnouncer:
    def __init__(self) -> None:
        self._listeners_: dict[int, list[queue.Queue[EventUpdate]]] = {}

    def add_listener(self, player_id: int) -> queue.Queue[EventUpdate]:
        q: queue.Queue[EventUpdate] = queue.Queue[EventUpdate](maxsize=1024)
        ql: list[queue.Queue[EventUpdate]] = self._listeners_.get(player_id, [])
        ql.append(q)
        self._listeners_[player_id] = ql
        return q

    def remove_listener(self, q: queue.Queue[EventUpdate]) -> None:
        for ql in self._listeners_.values():
            _ = ql.remove(q)

    def announce(self, update: EventUpdate, targets: list[int] | None = None):
        to_remove: list[int] = []
        for p_id in targets or self._listeners_.keys():
            ql = self._listeners_.get(p_id)
            if ql is None:
                continue
            for i in reversed(range(len(ql))):
                try:
                    ql[i].put_nowait(update)
                except queue.Full:
                    del ql[i]
            if len(ql) == 0:
                to_remove.append(p_id)
        for p_id in to_remove:
            del self._listeners_[p_id]
