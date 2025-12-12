from .constants import CARDS_FOR_TOKHM_BEZAR, CARDS_FOR_JOJOO_BEZAR

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
            print(f"Player {player.name} does not have enough {kind} cards to give for Tokhm.")
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
            print(f"Player {player.name} does not have enough {kind} cards to give for Jojo.")
            return

    for card in player.hand[:]:  # Iterate over a copy of the hand
        if card.kind in cards_to_remove and cards_to_remove[card.kind] > 0:
            player.hand.remove(card)
            cards_to_remove[card.kind] -= 1
            deck.not_in_deck_cards.append(card)
            deck.num_not_in_deck_cards += 1
            if all(count == 0 for count in cards_to_remove.values()):
                break
    