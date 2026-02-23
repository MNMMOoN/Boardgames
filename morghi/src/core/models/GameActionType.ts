/**
 * Types of game actions.
 */
export const GameActionType = {
  SkipTurn: 'SkipTurn',
  LayEgg: 'LayEgg',
  HatchEgg: 'HatchEgg',
  FoxSteal: 'FoxSteal',
  SnakeEat: 'SnakeEat',
  TrapKill: 'TrapKill',
  DefendFoxSteal: 'DefendFoxSteal',
} as const

export type GameActionType = (typeof GameActionType)[keyof typeof GameActionType]
