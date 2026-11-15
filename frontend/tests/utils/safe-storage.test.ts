import { describe, expect, it } from "vitest";

import { createSafeStorage } from "@/utils/safe-storage";

const BLOCKED = {
  getItem() {
    throw new Error("Blocked");
  },
  removeItem() {
    throw new Error("Blocked");
  },
  setItem() {
    throw new Error("Blocked");
  },
} as unknown as Storage;

describe("createSafeStorage", () => {
  it("reads and writes the underlying storage", () => {
    window.localStorage.clear();
    const storage = createSafeStorage(() => window.localStorage);

    storage.setItem("key", "value");

    expect(window.localStorage.getItem("key")).toBe("value");
    expect(storage.getItem("key")).toBe("value");
  });

  it("returns null for a key that is not stored", () => {
    expect(createSafeStorage(() => window.localStorage).getItem("missing")).toBeNull();
  });

  it("keeps values in memory when the storage is blocked", () => {
    const storage = createSafeStorage(() => BLOCKED);

    storage.setItem("key", "value");

    expect(storage.getItem("key")).toBe("value");

    storage.removeItem("key");

    expect(storage.getItem("key")).toBeNull();
  });

  it("copes with the storage accessor itself throwing", () => {
    const storage = createSafeStorage(() => {
      throw new Error("Blocked");
    });

    storage.setItem("key", "value");

    expect(storage.getItem("key")).toBe("value");
  });
});
