import { describe, expect, it } from "vitest";

import { topicTitle } from "@/features/course/utils/topic-title";

describe("topicTitle", () => {
  it.each([
    ["spine", "Everyday talk"],
    ["food", "Food"],
    ["hobbies", "Hobbies"],
    ["weather", "Weather"],
    ["family", "Family"],
    ["home", "Home"],
    ["work", "Work"],
    ["places", "Places"],
    ["time", "Time"],
  ])("names %s as %s", (name, title) => {
    expect(topicTitle(name)).toBe(title);
  });
});
