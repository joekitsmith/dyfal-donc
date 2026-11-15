import { useMutation } from "@tanstack/react-query";

import { unwrap } from "@/api/api-error";
import { apiClient } from "@/api/client";

import type { ReportedOutcome } from "../types";

export type OutcomeSubmission = {
  readonly outcome: ReportedOutcome;
  readonly selectionId: string;
};

export function useSubmitOutcome() {
  return useMutation({
    mutationFn: async ({ outcome, selectionId }: OutcomeSubmission) =>
      unwrap(await apiClient.POST("/me/outcomes", { body: { outcome, selection_id: selectionId } })),
  });
}
