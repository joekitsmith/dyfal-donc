import { describe, expect, it } from "vitest";

import { readStoredLearnerId, storeLearnerId } from "@/features/learner/api/learner-storage";
import { LEARNER_STORAGE_KEY } from "@/features/learner/constants";

import { MemoryStorage } from "../../../mocks/memory-storage";

const LEARNER_ID = "4f1d2c1e-6a0e-4a53-8f1b-0c6b6d5f6a11";

describe("readStoredLearnerId", () => {
  it("returns what was stored", () => {
    const storage = new MemoryStorage();

    storeLearnerId(storage, LEARNER_ID);

    expect(readStoredLearnerId(storage)).toBe(LEARNER_ID);
  });

  it("returns null when nothing is stored", () => {
    expect(readStoredLearnerId(new MemoryStorage())).toBeNull();
  });

  it("returns null for a value that is not an id", () => {
    const storage = new MemoryStorage();

    storage.setItem(LEARNER_STORAGE_KEY, "not-an-id");

    expect(readStoredLearnerId(storage)).toBeNull();
  });
});
