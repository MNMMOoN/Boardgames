/**
 * Playing cards in the game.
 */
export const Card = {
  Hen: 'Hen',
  Rooster: 'Rooster',
  Nest: 'Nest',
  Fox: 'Fox',
  Snake: 'Snake',
  Trap: 'Trap',
} as const

export type Card = (typeof Card)[keyof typeof Card]

/** Animal cards that can be killed by Trap (Hen, Rooster, Snake, Fox). */
export const ANIMAL_CARDS: Card[] = [
  Card.Hen,
  Card.Rooster,
  Card.Snake,
  Card.Fox,
]
