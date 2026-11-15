import { ApiError } from "@/api/api-error";

import { SEND_FAILED_MESSAGE, TOO_MANY_REPORTS_MESSAGE, TOO_MANY_REPORTS_STATUS } from "../constants";

/** What to tell the learner when the report was not sent. */
export function sendFailureMessage(error: Error): string {
  return error instanceof ApiError && error.status === TOO_MANY_REPORTS_STATUS
    ? TOO_MANY_REPORTS_MESSAGE
    : SEND_FAILED_MESSAGE;
}
