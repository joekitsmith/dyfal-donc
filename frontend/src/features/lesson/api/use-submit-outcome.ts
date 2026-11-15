import { useMutation } from "@tanstack/react-query";

import { unwrap } from "@/api/api-error";
import { apiClient } from "@/api/client";

import type { ReportedOutcome } from "../types";

import { RETRY_DELAYS_MILLISECONDS } from "../constants";
import { isRetryable } from "../utils/is-retryable";

export type OutcomeSubmission = {
  readonly outcome: ReportedOutcome;
  readonly selectionId: string;
};

export function useSubmitOutcome() {
  // Sending the answer again is safe: the server says it was already answered. With the screen
  // locked, a brief failure should not stop the lesson
  return useMutation({
    mutationFn: async ({ outcome, selectionId }: OutcomeSubmission) =>
      unwrap(await apiClient.POST("/me/outcomes", { body: { outcome, selection_id: selectionId } })),
    retry: (failures, error) => failures < RETRY_DELAYS_MILLISECONDS.length && isRetryable(error),
    retryDelay: (failures) => RETRY_DELAYS_MILLISECONDS[Math.min(failures, RETRY_DELAYS_MILLISECONDS.length - 1)] ?? 0,
  });
}
