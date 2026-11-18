import { afterEach, describe, expect, it, vi } from "vitest";

import {
  askToConfirm,
  cancelled,
  clearAccountSwitched,
  hasSwitchedAccount,
  leaveAccountScreen,
  noteAccountSwitched,
  pendingAction,
  stayOnAccountScreen,
} from "@/features/auth/stores/step-up-store";
import { StepUpCancelledError } from "@/features/auth/utils/step-up";

afterEach(() => {
  vi.useRealTimers();
  clearAccountSwitched();
  cancelled();
});

describe("askToConfirm", () => {
  it("keeps the first action while it waits, and goes back to none when it is over", async () => {
    const first = askToConfirm("add_passkey");

    void askToConfirm("delete_account");
    expect(pendingAction()).toBe("add_passkey");

    cancelled();
    await expect(first).rejects.toThrow(StepUpCancelledError);
    expect(pendingAction()).toBeNull();
  });
});

describe("the notice that confirming switched accounts", () => {
  it("is there from when it is noted until it is cleared", () => {
    expect(hasSwitchedAccount()).toBe(false);

    noteAccountSwitched();
    expect(hasSwitchedAccount()).toBe(true);

    clearAccountSwitched();
    expect(hasSwitchedAccount()).toBe(false);
  });

  it("goes a moment after the screen is left", () => {
    vi.useFakeTimers();
    noteAccountSwitched();

    leaveAccountScreen();
    expect(hasSwitchedAccount()).toBe(true);

    vi.runAllTimers();
    expect(hasSwitchedAccount()).toBe(false);
  });

  it("stays when the screen is shown again straight away", () => {
    vi.useFakeTimers();
    noteAccountSwitched();

    leaveAccountScreen();
    stayOnAccountScreen();
    vi.runAllTimers();

    expect(hasSwitchedAccount()).toBe(true);
  });
});
