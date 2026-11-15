import type { KeyValueStorage } from "@/utils/safe-storage";

export class MemoryStorage implements KeyValueStorage {
  readonly values = new Map<string, string>();

  getItem(key: string): null | string {
    return this.values.get(key) ?? null;
  }

  setItem(key: string, value: string): void {
    this.values.set(key, value);
  }

  removeItem(key: string): void {
    this.values.delete(key);
  }
}
