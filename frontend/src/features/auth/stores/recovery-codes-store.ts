const NONE: readonly string[] = [];

let codes = NONE;
const listeners = new Set<() => void>();

/** The recovery codes waiting to be shown. They live only in memory, and only until they are saved. */
export function getRecoveryCodes(): readonly string[] {
  return codes;
}

export function showRecoveryCodes(next: readonly string[]): void {
  codes = next;
  notify();
}

export function clearRecoveryCodes(): void {
  codes = NONE;
  notify();
}

export function subscribeToRecoveryCodes(listener: () => void): () => void {
  listeners.add(listener);

  return () => {
    listeners.delete(listener);
  };
}

function notify(): void {
  for (const listener of listeners) {
    listener();
  }
}
