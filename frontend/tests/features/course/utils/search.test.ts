import { describe, expect, it } from "vitest";

import type { CourseItem, TopicProgress } from "@/features/course/types";

import { normaliseSearchText, searchItems } from "@/features/course/utils/search";

function item(id: string, welsh: string, english: string, forms: string[] = []): CourseItem {
  return { english, forms, id, welsh };
}

function topic(name: string, words: CourseItem[]): TopicProgress {
  return { exercises_answered: 0, is_current: false, name, phrases: [], sayable: [], started: true, words };
}

const TOPICS = [
  topic("spine", [item("lex:heddiw", "heddiw", "today", ["heddi"]), item("lex:ty", "tŷ", "house", ["tai"])]),
  topic("weather", [item("lex:gwynt", "gwynt", "wind")]),
];

describe("normaliseSearchText", () => {
  it("ignores case, accents and surrounding space", () => {
    expect(normaliseSearchText("  ŴYR ")).toBe("wyr");
    expect(normaliseSearchText("tŷ")).toBe("ty");
  });

  it("keeps an apostrophe", () => {
    expect(normaliseSearchText("Dw i'n")).toBe("dw i'n");
  });
});

describe("searchItems", () => {
  it("finds an item by its English", () => {
    expect(searchItems(TOPICS, "Wind").map(({ item: found }) => found.id)).toEqual(["lex:gwynt"]);
  });

  it("finds an item by its Welsh, ignoring accents", () => {
    expect(searchItems(TOPICS, "ty").map(({ item: found }) => found.id)).toEqual(["lex:ty"]);
  });

  it("finds an item by another form", () => {
    expect(searchItems(TOPICS, "tai").map(({ item: found }) => found.id)).toEqual(["lex:ty"]);
  });

  it("says which topic each match is in, in teaching order", () => {
    expect(searchItems(TOPICS, "w").map(({ topic: name }) => name)).toEqual(["spine", "weather"]);
  });

  it("finds nothing for an empty search or no match", () => {
    expect(searchItems(TOPICS, "  ")).toEqual([]);
    expect(searchItems(TOPICS, "elephant")).toEqual([]);
  });
});
