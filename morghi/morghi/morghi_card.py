class Card:
    def __init__(self, name, kind, max_plays=None):
        """
        Parameters:
            name (str)        – name of the card
            kind (str)        – category of the card ("attack", "defense", "magic", etc.)
            max_plays (int)   – how many times this card can be used
        """
        self.name = name
        self.kind = kind
        self.max_plays = max_plays
        self.times_played = 0
        self.playable = True

    def can_play(self):
        """Check if the card can still be played."""
        if self.max_plays is None:
            return self.playable
        
        if self.times_played > self.max_plays:
            self.playable = False

        return self.playable

    def play(self, target=None):
        """General play method (to be overridden by child classes)."""
        if not self.can_play():
            print(f"{self.name} cannot be played anymore.")
            return

        self.times_played += 1
        if self.max_plays is None:
            print(f"{self.name} was played! (used {self.times_played})")
        else:
            print(f"{self.name} was played! (used {self.times_played}/{self.max_plays})")
        # Child classes override this to implement functionality