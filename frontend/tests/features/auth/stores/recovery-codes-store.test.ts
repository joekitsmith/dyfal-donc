import { afterEach, describe, expect, it, vi } from "vitest";

import {
  clearRecoveryCodes,
  getRecoveryCodes,
  showRecoveryCodes,
  subscribeToRecoveryCodes,
} from "@/features/auth/stores/recovery-codes-store";

afterEach(() => {
  clearRecoveryCodes();
});

describe("the recovery codes store", () => {
  it("holds the codes until they are cleared", () => {
    expect(getRecoveryCodes()).toEqual([]);

    showRecoveryCodes(["AAAA-BBBB-CCCC-DDDD"]);
    expect(getRecoveryCodes()).toEqual(["AAAA-BBBB-CCCC-DDDD"]);

    clearRecoveryCodes();
    expect(getRecoveryCodes()).toEqual([]);
  });

  it("tells a listener when the codes change, until it unsubscribes", () => {
    const listener = vi.fn();
    const unsubscribe = subscribeToRecoveryCodes(listener);

    showRecoveryCodes(["AAAA-BBBB-CCCC-DDDD"]);
    unsubscribe();
    clearRecoveryCodes();

    expect(listener).toHaveBeenCalledTimes(1);
  });
});
