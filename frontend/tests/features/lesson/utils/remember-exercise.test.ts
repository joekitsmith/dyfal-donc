import { describe, expect, it } from "vitest";

import type { LessonExercise } from "@/features/lesson/types";

import { rememberExercise } from "@/features/lesson/utils/remember-exercise";

function exercise(exerciseId: string, selectionId = `selection-${exerciseId}`): LessonExercise {
  return {
    audio: { english: "/e", welsh_slow: "/s", welsh_standard: "/w" },
    english: exerciseId,
    exerciseId,
    selectionId,
    welsh: exerciseId,
  };
}

const ids = (exercises: readonly LessonExercise[]) => exercises.map((remembered) => remembered.exerciseId);

describe("rememberExercise", () => {
  it("puts the newest first", () => {
    expect(ids(rememberExercise([exercise("a")], exercise("b")))).toEqual(["b", "a"]);
  });

  it("keeps only the current exercise and the two before it", () => {
    const recent = [exercise("c"), exercise("b"), exercise("a")];

    expect(ids(rememberExercise(recent, exercise("d")))).toEqual(["d", "c", "b"]);
  });

  it("moves a sentence seen again to the front instead of listing it twice", () => {
    const recent = [exercise("b"), exercise("a")];

    const remembered = rememberExercise(recent, exercise("a", "selection-again"));

    expect(ids(remembered)).toEqual(["a", "b"]);
    expect(remembered[0]?.selectionId).toBe("selection-again");
  });
});
