import { describe, expect, it } from "vitest";

import type { Passkey } from "@/features/auth/types";

import { describePasskey, passkeyName } from "@/features/auth/utils/describe-passkey";

const NOW = new Date(2026, 2, 10, 15, 0);

function passkey(overrides: Partial<Passkey>): Passkey {
  return {
    createdAt: new Date(2026, 2, 3, 9, 0).toISOString(),
    id: "p",
    label: "My phone",
    lastUsedAt: null,
    ...overrides,
  };
}

describe("describePasskey", () => {
  it("says when it was added and that it was used today", () => {
    const used = new Date(2026, 2, 10, 8, 0).toISOString();

    expect(describePasskey(passkey({ lastUsedAt: used }), NOW)).toBe("Added 3 March 2026 · last used today");
  });

  it("says yesterday for the day before, whatever the time", () => {
    const used = new Date(2026, 2, 9, 23, 59).toISOString();

    expect(describePasskey(passkey({ lastUsedAt: used }), NOW)).toBe("Added 3 March 2026 · last used yesterday");
  });

  it("writes an older day out", () => {
    const used = new Date(2026, 2, 5, 12, 0).toISOString();

    expect(describePasskey(passkey({ lastUsedAt: used }), NOW)).toBe("Added 3 March 2026 · last used 5 March 2026");
  });

  it("says when it was never used", () => {
    expect(describePasskey(passkey({}), NOW)).toBe("Added 3 March 2026 · never used");
  });
});

describe("passkeyName", () => {
  it("is the name it was given", () => {
    expect(passkeyName(passkey({ label: "My phone" }))).toBe("My phone");
  });

  it("is Unnamed passkey for the name the server gives one that was not named", () => {
    expect(passkeyName(passkey({ label: "Passkey" }))).toBe("Unnamed passkey");
  });
});
