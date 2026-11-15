import { ApiError } from "@/api/api-error";
import { ClipUnavailableError } from "@/api/clips";

import type { FailureCause } from "../types";

import { NOT_FOUND_STATUS, SERVICE_UNAVAILABLE_STATUS, UNAUTHORIZED_STATUS } from "../constants";

export function failureCause(error: unknown): FailureCause {
  if (error instanceof ApiError && (error.status === NOT_FOUND_STATUS || error.status === UNAUTHORIZED_STATUS)) {
    return "learner_missing";
  }

  if (error instanceof ClipUnavailableError && error.status === SERVICE_UNAVAILABLE_STATUS) {
    return "speech_unavailable";
  }

  return "other";
}
