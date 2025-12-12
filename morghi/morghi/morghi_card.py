class Card:
    def __init__(self, name: str, is_animal: bool | None, max_plays: int = 0):
        """
        Parameters:
            name (str)        – name of the card
            kind (str)        – category of the card ("attack", "defense", "magic", etc.)
            max_plays (int)   – how many times this card can be used
        """
        self.name = name
        self.is_animal = None
        self.max_plays = max_plays
        self.times_played = 0
        self._playable = True

    def can_play(self):
        """Check if the card can still be played."""
        if self.max_plays is None:
            return self._playable
        
        if self.times_played > self.max_plays:
            self._playable = False

        return self._playable