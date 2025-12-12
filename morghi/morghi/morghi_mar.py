from morghi_animal import Animal

class Mar(Animal):
    # Class-level list to track all Morgh instances
    instances = []

    def __init__(self, name="Morgh", kind="Morgh", max_plays=None):
        super().__init__(name, kind, max_plays)
        # Add this instance to the list
        Mar.instances.append(self)

    def play(self, target=None):
        if not self.can_play():
            print(f"{self.name} cannot be played anymore.")
            return

        self.times_played += 1

        # Count how many Morgh have been played at least once
        played_count = sum(1 for m in Mar.instances if m.times_played > 0)

        if played_count >= 2:
            print(f"Two or more Mar are in play! Special action triggered!")
            # Do your special behavior here
        else:
            print(f"{self.name} is playing normally. (used {self.times_played})")