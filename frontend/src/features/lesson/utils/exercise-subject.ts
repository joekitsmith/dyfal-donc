import type { ReportSubject } from "@/features/problem-report";

import type { LessonExercise } from "../types";

export function exerciseSubject(exercise: LessonExercise): ReportSubject {
  return {
    audio: exercise.audio.welsh_standard,
    english: exercise.english,
    id: exercise.exerciseId,
    kind: "sentence",
    welsh: exercise.welsh,
  };
}
