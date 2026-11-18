import { describe, expect, it } from "vitest";

import { parseSlots } from "@/utils/slots";

describe("parseSlots", () => {
  it("leaves text with no slot as it is", () => {
    expect(parseSlots("Dw i'n hapus")).toEqual([{ kind: "text", text: "Dw i'n hapus" }]);
  });

  it("names a slot in lower case", () => {
    expect(parseSlots("Dw i'n moyn [VERB]")).toEqual([
      { kind: "text", text: "Dw i'n moyn " },
      { kind: "slot", name: "verb" },
    ]);
  });

  it("keeps English that runs on after a slot", () => {
    expect(parseSlots("I like [VERB]ing it")).toEqual([
      { kind: "text", text: "I like " },
      { kind: "slot", name: "verb" },
      { kind: "text", text: "ing it" },
    ]);
  });

  it("finds a slot at the start and more than one", () => {
    expect(parseSlots("[NOUN] and [ADJECTIVE]")).toEqual([
      { kind: "slot", name: "noun" },
      { kind: "text", text: " and " },
      { kind: "slot", name: "adjective" },
    ]);
  });

  it("does not treat other brackets as slots", () => {
    expect(parseSlots("a [word] here")).toEqual([{ kind: "text", text: "a [word] here" }]);
  });

  it("is empty for empty text", () => {
    expect(parseSlots("")).toEqual([]);
  });
});
