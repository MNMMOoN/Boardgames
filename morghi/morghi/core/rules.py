CARD_MORGH: str = "Morgh"
CARD_KHOROS: str = "Khoros"
CARD_ROBAH: str = "Robah"
CARD_MAR: str = "Mar"
CARD_LOUNE: str = "Loune"
CARD_TALE: str = "Tale"

# NUM CONSTANTS
NUM_OF_PLAYERS: int = 4
MAX_NUM_OF_CARDS_IN_HAND: int = 4
MIN_NUM_OF_CARDS_IN_HAND: int = 4
STARTING_NUM_OF_CARDS_IN_HAND: int = MIN_NUM_OF_CARDS_IN_HAND
NUM_OF_MORGHS: int = 11
NUM_OF_KHOROSES: int = 11
NUM_OF_ROBAHS: int = 7
NUM_OF_MARS: int = 4
NUM_OF_TALES: int = 6
NUM_OF_LOUNES: int = 11
NUM_OF_TOKHMS: int = 60

# AVAILABLE CARDS IN THE GAME
AVAILABLE_ANIMAL_CARDS: dict[str, int] = {
    CARD_MORGH: NUM_OF_MORGHS,
    CARD_KHOROS: NUM_OF_KHOROSES,
    CARD_ROBAH: NUM_OF_ROBAHS,
    CARD_MAR: NUM_OF_MARS,
}

AVAILABLE_NONANIMAL_CARDS: dict[str, int] = {
    CARD_LOUNE: NUM_OF_LOUNES,
    CARD_TALE: NUM_OF_TALES,
}

# AVAILABLE_CARDS = {**AVAILABLE_ANIMAL_CARDS, **AVAILABLE_NONANIMAL_CARDS}

AVAILABLE_CARDS: dict[str, dict[str, int]] = {
    "animal": AVAILABLE_ANIMAL_CARDS,
    "nonanimal": AVAILABLE_NONANIMAL_CARDS,
}

TOTAL_NUM_CARDS: int = sum(map(lambda x: sum(x.values()), AVAILABLE_CARDS.values()))

# Rules
MAX_GAME_PLAYERS: int = 8
CARDS_FOR_TOKHM_BEZAR: dict[str, int] = {CARD_MORGH: 1, CARD_KHOROS: 1, CARD_LOUNE: 1}
CARDS_FOR_JOJOO_BEZAR: dict[str, int] = {CARD_MORGH: 2}
CARDS_FOR_TOKHM_BEDOZED: dict[str, int] = {CARD_ROBAH: 1}
CARDS_FOR_DEFENDING_TOKHM_BEDOZED: dict[str, int] = {CARD_KHOROS: 2}
CARDS_FOR_TOKHM_BESHKAN: dict[str, int] = {CARD_MAR: 2}
CARDS_FOR_DEFENDING_TOKHM_BESHKAN: dict[str, int] = {}


def tokhm_bezar(player, deck):
    """
    Give birth to a new Tokhm (egg) card for the player.
    The player should give a CARDS_FOR_TOKHM_BEZAR to the deck.
    """
    player.num_of_tokhms += 1
    # Remove CARDS_FOR_TOKHM_BEZAR from player's hand
    cards_to_remove = CARDS_FOR_TOKHM_BEZAR.copy()

    # Player have all the cards in hand
    available_kinds = [card.kind for card in player.hand]
    for kind in cards_to_remove:
        if available_kinds.count(kind) < cards_to_remove[kind]:
            print(
                f"Player {player.name} does not have enough {kind} cards to give for Tokhm."
            )
            return

    for card in player.hand[:]:  # Iterate over a copy of the hand
        if card.kind in cards_to_remove and cards_to_remove[card.kind] > 0:
            player.hand.remove(card)
            cards_to_remove[card.kind] -= 1
            deck.not_in_deck_cards.append(card)
            deck.num_not_in_deck_cards += 1
            if all(count == 0 for count in cards_to_remove.values()):
                break


def jojoo_bezar(player, deck):
    """
    Give birth to a new Jojo (chick) card for the player.
    The player should give CARDS_FOR_JOJOO_BEZAR to the deck.
    """
    player.num_of_jojos += 1
    player.num_of_tokhms -= 1
    # Remove CARDS_FOR_JOJOO_BEZAR from player's hand
    cards_to_remove = CARDS_FOR_JOJOO_BEZAR.copy()

    # Player have all the cards in hand
    available_kinds = [card.kind for card in player.hand]
    for kind in cards_to_remove:
        if available_kinds.count(kind) < cards_to_remove[kind]:
            print(
                f"Player {player.name} does not have enough {kind} cards to give for Jojo."
            )
            return

    for card in player.hand[:]:  # Iterate over a copy of the hand
        if card.kind in cards_to_remove and cards_to_remove[card.kind] > 0:
            player.hand.remove(card)
            cards_to_remove[card.kind] -= 1
            deck.not_in_deck_cards.append(card)
            deck.num_not_in_deck_cards += 1
            if all(count == 0 for count in cards_to_remove.values()):
                break


def tokhm_bedozed(player1, player2, deck):
    """
    Steel one Tokhm from th eother players hand
    """
    player1_hand = [card.kind for card in player1.hand]
    player2_hand = [card.kind for card in player2.hand]

    for kind, count in CARDS_FOR_TOKHM_BEDOZED.items():
        if player1_hand.count(kind) < count:
            print(
                f"Player {player1.name} does not have enough {kind} cards to give for Tokhm Bedozed."
            )
            return

        for _ in range(count):
            player1.hand.remove(kind)
            deck.not_in_deck_cards.append(kind)
            deck.num_not_in_deck_cards += 1

    can_defend = True
    for kind, count in CARDS_FOR_DEFENDING_TOKHM_BEDOZED.items():
        if player2_hand.count(kind) < count:
            print(
                f"Player {player2.name} does not have enough {kind} cards to defend for Tokhm Bedozed."
            )
            can_defend = False

    if can_defend:
        for kind, count in CARDS_FOR_DEFENDING_TOKHM_BEDOZED.items():
            for _ in range(count):
                player2.hand.remove(kind)
                deck.not_in_deck_cards.append(kind)
                deck.num_not_in_deck_cards += 1
        print(f"Player {player2.name} defends against Tokhm Bedozed.")

    else:
        # Player 1 steals one Tokhm from player 2
        if player2.num_of_tokhms > 0:
            player2.num_of_tokhms -= 1
            player1.num_of_tokhms += 1
            print(f"Player {player1.name} steals one Tokhm from {player2.name}.")
        else:
            print(f"Player {player2.name} does not have any Tokhm to steal.")


def tokhm_beshkan(player1, player2, n, deck):
    """
    Destroy one or two Tokhm from the other player's hand
    """
    player1_hand = [card.kind for card in player1.hand]
    player2_hand = [card.kind for card in player2.hand]

    if n != 2:
        print("You can only destroy 2 Tokhm.")
        return

    for kind, count in CARDS_FOR_TOKHM_BESHKAN.items():
        if player1_hand.count(kind) < count:
            print(
                f"Player {player1.name} does not have enough {kind} cards to give for Tokhm Beshkan."
            )
            return

        for _ in range(count):
            player1.hand.remove(kind)
            deck.not_in_deck_cards.append(kind)
            deck.num_not_in_deck_cards += 1

    can_defend = True
    for kind, count in CARDS_FOR_DEFENDING_TOKHM_BESHKAN.items():
        if player2_hand.count(kind) < count:
            print(
                f"Player {player2.name} does not have enough {kind} cards to defend for Tokhm Beshkan."
            )
            can_defend = False

    if can_defend:
        for kind, count in CARDS_FOR_DEFENDING_TOKHM_BESHKAN.items():
            for _ in range(count):
                player2.hand.remove(kind)
                deck.not_in_deck_cards.append(kind)
                deck.num_not_in_deck_cards += 1
        print(f"Player {player2.name} defends against Tokhm Beshkan.")

    else:
        # Player 1 destroys one or two Tokhm from player 2
        if player2.num_of_tokhms > 0:
            destroyed_tokhms = min(n, player2.num_of_tokhms)
            player2.num_of_tokhms -= destroyed_tokhms
            print(
                f"Player {player1.name} destroys {destroyed_tokhms} Tokhm from {player2.name}."
            )
        else:
            print(f"Player {player2.name} does not have any Tokhm to destroy.")
