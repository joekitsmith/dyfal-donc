import type { LessonExercise } from "../types";

import { MAX_RECENT_EXERCISES } from "../constants";

/** The exercises seen lately, newest first. A sentence seen again moves to the front instead of appearing twice. */
export function rememberExercise(
  recent: readonly LessonExercise[],
  exercise: LessonExercise,
): readonly LessonExercise[] {
  return [exercise, ...recent.filter((earlier) => earlier.exerciseId !== exercise.exerciseId)].slice(
    0,
    MAX_RECENT_EXERCISES,
  );
}
