import { useMutation } from "@tanstack/react-query";

import { unwrap } from "@/api/api-error";
import { apiClient } from "@/api/client";

import type { ReportedOutcome } from "../types";

export type OutcomeSubmission = {
  readonly outcome: ReportedOutcome;
  readonly selectionId: string;
};

export function useSubmitOutcome(learnerId: string) {
  return useMutation({
    mutationFn: async ({ outcome, selectionId }: OutcomeSubmission) =>
      unwrap(
        await apiClient.POST("/learners/{learner_id}/outcomes", {
          body: { outcome, selection_id: selectionId },
          params: { path: { learner_id: learnerId } },
        }),
      ),
  });
}
