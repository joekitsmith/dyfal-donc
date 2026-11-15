import { describe, expect, it } from "vitest";

import type { CourseItem, TopicProgress } from "@/features/course/types";

import { describeTopic } from "@/features/course/utils/describe-topic";
import { formatFirstMet } from "@/features/course/utils/format-first-met";

function items(amount: number): CourseItem[] {
  return Array.from({ length: amount }, (_, index) => ({
    english: "x",
    forms: [],
    id: `lex:${index}`,
    welsh: "x",
  }));
}

function topic(words: number, phrases: number, answered: number): TopicProgress {
  return {
    exercises_answered: answered,
    is_current: false,
    name: "food",
    phrases: items(phrases),
    sayable: [],
    started: true,
    words: items(words),
  };
}

describe("describeTopic", () => {
  it("counts what was met", () => {
    expect(describeTopic(topic(12, 4, 42))).toBe("12 words · 4 ways of saying things · 42 exercises answered");
  });

  it("uses the singular for one", () => {
    expect(describeTopic(topic(1, 1, 1))).toBe("1 word · 1 way of saying things · 1 exercise answered");
  });
});

describe("formatFirstMet", () => {
  it("writes the day in full", () => {
    expect(formatFirstMet("2026-03-03T12:00:00Z")).toBe("3 March 2026");
  });
});
