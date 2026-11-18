import { describe, expect, it } from "vitest";

import { shortenSlots } from "@/features/learning-session/utils/shorten-slots";

describe("shortenSlots", () => {
  it.each([
    ["siarad", "siarad"],
    ["Dw i'n moyn [VERB]", "Dw i'n moyn…"],
    ["Mae [NOUN] yn [VERB]", "Mae… yn…"],
    ["[NOUN] yn dda", "… yn dda"],
  ])("shows %s as %s", (welsh, shown) => {
    expect(shortenSlots(welsh)).toBe(shown);
  });
});
