import { describe, expect, it } from "vitest";

import { countWords } from "@/utils/count-words";

describe("countWords", () => {
  it.each([
    ["", 0],
    ["siarad", 1],
    ["Galla i fynd", 3],
    ["  Galla   i fynd  ", 3],
  ])("counts the words of %j as %d", (sentence, words) => {
    expect(countWords(sentence)).toBe(words);
  });
});
