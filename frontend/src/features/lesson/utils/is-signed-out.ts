import { ApiError } from "@/api/api-error";

import { UNAUTHORIZED_STATUS } from "../constants";

/** The server no longer knows who is asking: the session ended, so there is nothing to retry. */
export function isSignedOut(error: unknown): boolean {
  return error instanceof ApiError && error.status === UNAUTHORIZED_STATUS;
}
