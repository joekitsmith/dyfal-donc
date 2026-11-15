import { useMutation } from "@tanstack/react-query";

import { unwrap } from "@/api/api-error";
import { apiClient } from "@/api/client";

import type { LessonExercise } from "../types";

export type NextExercise =
  | { readonly exercise: LessonExercise; readonly kind: "exercise" }
  | { readonly kind: "nothing_eligible"; readonly reason: string };

export function useNextExercise(learnerId: string) {
  return useMutation({
    mutationFn: async (): Promise<NextExercise> => {
      const offered = unwrap(
        await apiClient.GET("/learners/{learner_id}/next", { params: { path: { learner_id: learnerId } } }),
      );

      if (offered.kind === "nothing_eligible") {
        return { kind: "nothing_eligible", reason: offered.reason };
      }

      return {
        exercise: {
          audio: {
            english: offered.audio.english,
            welsh: offered.audio.welsh,
            welsh_slow: offered.audio.welsh_slow,
          },
          english: offered.english,
          selectionId: offered.selection_id,
          welsh: offered.welsh,
        },
        kind: "exercise",
      };
    },
  });
}
