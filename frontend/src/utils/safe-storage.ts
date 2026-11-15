export type KeyValueStorage = {
  readonly getItem: (key: string) => null | string;
  readonly removeItem: (key: string) => void;
  readonly setItem: (key: string, value: string) => void;
};

/**
 * Storage that never throws. Browsers can refuse access to localStorage (private windows,
 * blocked site data), so values then live in memory for the rest of the page's life.
 */
export function createSafeStorage(getStorage: () => Storage): KeyValueStorage {
  const memory = new Map<string, string>();

  return {
    getItem(key) {
      try {
        return getStorage().getItem(key);
      } catch {
        return memory.get(key) ?? null;
      }
    },
    removeItem(key) {
      try {
        getStorage().removeItem(key);
      } catch {
        memory.delete(key);
      }
    },
    setItem(key, value) {
      try {
        getStorage().setItem(key, value);
      } catch {
        memory.set(key, value);
      }
    },
  };
}

export const browserStorage = createSafeStorage(() => window.localStorage);
