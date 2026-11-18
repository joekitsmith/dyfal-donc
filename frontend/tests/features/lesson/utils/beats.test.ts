import { describe, expect, it } from "vitest";

import { beatCount } from "@/features/lesson/utils/beats";
import { countWords } from "@/features/lesson/utils/count-words";

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

describe("beatCount", () => {
  it("is the number of words and three more", () => {
    expect(beatCount("Galla i fynd")).toBe(6);
    expect(beatCount("Dw i eisiau mynd i'r siop heddiw")).toBe(10);
  });
});
