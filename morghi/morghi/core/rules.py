class Cards:
    FOX: str = "Robah"
    HEN: str = "Morgh"
    NEST: str = "Loune"
    ROOSTER: str = "Khoros"
    SNAKE: str = "Mar"
    TRAP: str = "Tale"

    HEN_COUNT: int = 11
    ROOSTER_COUNT: int = 11
    FOX_COUNT: int = 7
    SNAKE_COUNT: int = 4
    TRAP_COUNT: int = 6
    NEST_COUNT: int = 11
    SCORE_COUNT: int = 60

    @staticmethod
    def all():
        return [
            card
            for card, count in {
                Cards.HEN: Cards.HEN_COUNT,
                Cards.ROOSTER: Cards.ROOSTER_COUNT,
                Cards.FOX: Cards.FOX_COUNT,
                Cards.SNAKE: Cards.SNAKE_COUNT,
                Cards.TRAP: Cards.TRAP_COUNT,
                Cards.NEST: Cards.NEST_COUNT,
            }.items()
            for _ in range(count)
        ]


class Rules:
    MAX_PLAYERS_COUNT: int = 8
    NUM_CARDS_IN_HAND: int = 4
    CARDS_TO_LAY_EGG: list[str] = [Cards.HEN, Cards.ROOSTER, Cards.NEST]
    CARDS_TO_HATCH_EGG: list[str] = [Cards.HEN, Cards.HEN]
    CARDS_TO_STEAL_EGG: list[str] = [Cards.FOX]
    CARDS_TO_DEFEND_EGG: list[str] = [Cards.ROOSTER, Cards.ROOSTER]
    CARDS_TO_BREAK_EGG: list[str] = [Cards.SNAKE, Cards.SNAKE]
    MAX_EGGS_TO_BREAK: int = 2
    CARDS_ALLOWED_TO_BE_KILLED_BY_TRAP: list[str] = [  # a.k.a. Animals
        Cards.HEN,
        Cards.ROOSTER,
        Cards.FOX,
        Cards.SNAKE,
    ]
