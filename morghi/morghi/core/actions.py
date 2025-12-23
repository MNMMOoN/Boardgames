import abc


class Action(abc.ABC):
    def __init__(self, name: str, card_indices: set[int]):
        self.name: str = name
        self.card_indices: set[int] = card_indices

    @staticmethod
    def create_from_dict(name: str, data: dict) -> Action:
        if name == SkipTurn.NAME:
            return SkipTurn.from_dict(data)
        elif name == LayEgg.NAME:
            return LayEgg.from_dict(data)
        elif name == StealEgg.NAME:
            return StealEgg.from_dict(data)
        elif name == DefendEgg.NAME:
            return DefendEgg.from_dict(data)
        elif name == BreakEgg.NAME:
            return BreakEgg.from_dict(data)
        else:
            raise ValueError(f"Unknown action '{name}'")


class SkipTurn(Action):
    NAME: str = "skip_turn"

    def __init__(self, card_indices: set[int]):
        super().__init__(
            name=SkipTurn.NAME,
            card_indices=card_indices,
        )

    @staticmethod
    def from_dict(data: dict) -> SkipTurn:
        return SkipTurn(card_indices=set(int(i) for i in data["card_indices"]))


class LayEgg(Action):
    NAME: str = "lay_egg"

    def __init__(self, card_indices: set[int]):
        super().__init__(
            name=StealEgg.NAME,
            card_indices=card_indices,
        )

    @staticmethod
    def from_dict(data: dict) -> LayEgg:
        return LayEgg(card_indices=set(int(i) for i in data["card_indices"]))


class StealEgg(Action):
    NAME: str = "steal_egg"

    def __init__(self, card_indices: set[int], target: int):
        super().__init__(
            name=StealEgg.NAME,
            card_indices=card_indices,
        )
        self.target = target

    @staticmethod
    def from_dict(data: dict) -> StealEgg:
        return StealEgg(
            card_indices=set(int(i) for i in data["card_indices"]),
            target=int(data["target"]),
        )


class DefendEgg(Action):
    NAME: str = "fox_defend"

    def __init__(self, card_indices: set[int], defender: int, does_defend: bool):
        super().__init__(
            name=DefendEgg.NAME,
            card_indices=card_indices,
        )
        self.defender = defender
        self.does_defend = does_defend

    @staticmethod
    def from_dict(data: dict) -> DefendEgg:
        return DefendEgg(
            card_indices=set(int(i) for i in data["card_indices"]),
            defender=int(data["defender"]),
            does_defend=bool(data["does_defend"]),
        )


class BreakEgg(Action):
    NAME: str = "break_egg"

    def __init__(self, card_indices: set[int], target: int):
        super().__init__(
            name=BreakEgg.NAME,
            card_indices=card_indices,
        )
        self.target = target

    @staticmethod
    def from_dict(data: dict) -> BreakEgg:
        return BreakEgg(
            card_indices=set(int(i) for i in data["card_indices"]),
            target=int(data["target"]),
        )
