import type { FailureCause } from "../types";

import { ERROR_MESSAGES, LEARNER_MISSING_MESSAGE, SPEECH_UNAVAILABLE_MESSAGE } from "../constants";

/** What to tell the learner when something failed: the cause if it is known, otherwise what was being done. */
export function errorMessage(context: keyof typeof ERROR_MESSAGES, cause: FailureCause): string {
  switch (cause) {
    case "learner_missing":
      return LEARNER_MISSING_MESSAGE;
    case "other":
      return ERROR_MESSAGES[context];
    case "speech_unavailable":
      return SPEECH_UNAVAILABLE_MESSAGE;
  }
}
