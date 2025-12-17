import typing as T
import queue


class EventUpdate(T.TypedDict):
    event: str
    data: T.Any


class EventAnnouncer:
    def __init__(self) -> None:
        self._listeners_: list[queue.Queue[EventUpdate]] = []

    def add_listener(self) -> queue.Queue[EventUpdate]:
        q: queue.Queue[EventUpdate] = queue.Queue[EventUpdate](maxsize=1024)
        self._listeners_.append(q)
        return q

    def remove_listener(self, q: queue.Queue[EventUpdate]) -> None:
        self._listeners_.remove(q)

    def announce(self, msg):
        # We broadcast the data string to all connected queues
        # iterating backwards to safely remove dead listeners
        for i in reversed(range(len(self._listeners_))):
            try:
                self._listeners_[i].put_nowait(msg)
            except queue.Full:
                del self._listeners_[i]
