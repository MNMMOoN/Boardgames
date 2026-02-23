/**
 * Interface for the observer pattern - easier handling of event subscriptions.
 */
export interface IEvent<T> {
  addListener(callback: (data: T) => void): void
  delListener(callback: (data: T) => void): void
}

/**
 * Implements IEvent - invokes all registered listeners when invoke() is called.
 */
export class Event<T> implements IEvent<T> {
  private listeners: Set<(data: T) => void> = new Set()

  addListener(callback: (data: T) => void): void {
    this.listeners.add(callback)
  }

  delListener(callback: (data: T) => void): void {
    this.listeners.delete(callback)
  }

  invoke(data: T): void {
    for (const cb of this.listeners) {
      cb(data)
    }
  }
}
