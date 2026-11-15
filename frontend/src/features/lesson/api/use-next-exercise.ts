import { useMutation } from "@tanstack/react-query";

import { unwrap } from "@/api/api-error";
import { apiClient } from "@/api/client";

import type { LessonExercise } from "../types";

export type NextExercise =
  { readonly exercise: LessonExercise; readonly kind: "exercise" } | { readonly kind: "nothing_eligible" };

export function useNextExercise() {
  return useMutation({
    mutationFn: async (): Promise<NextExercise> => {
      const offered = unwrap(await apiClient.POST("/me/next"));

      if (offered.kind === "nothing_eligible") {
        return { kind: "nothing_eligible" };
      }

      return {
        exercise: {
          audio: {
            english: offered.audio.english,
            welsh_slow: offered.audio.welsh.slow,
            welsh_standard: offered.audio.welsh.standard,
          },
          english: offered.english,
          exerciseId: offered.exercise_id,
          selectionId: offered.selection_id,
          welsh: offered.welsh,
        },
        kind: "exercise",
      };
    },
  });
}
