class Card:
    def __init__(self, name: str, is_animal: bool | None, max_plays: int = 0):
        self.name = name
        self.is_animal = is_animal
        self.max_plays = max_plays
        self.times_played = 0
        self._playable = True

    def can_play(self):
        if self.max_plays is None:
            return self._playable

        if self.times_played > self.max_plays:
            self._playable = False

        return self._playable
