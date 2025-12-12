from morghi_card import Card

class Animal(Card):
    def __init__(self, name, kind, max_plays=None):
        # Correct call to parent constructor
        super().__init__(name, kind, max_plays)
