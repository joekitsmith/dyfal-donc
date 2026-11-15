import { SERVER_ERROR_STATUS, SERVICE_UNAVAILABLE_STATUS } from "../constants";

/**
 * A failure that may pass: the network, or the server having a bad moment. A refusal (signed out,
 * already answered, expired, not found) would fail again, and 503 is the speech service being
 * down, which has its own message.
 */
export function isRetryable(error: unknown): boolean {
  const status =
    typeof error === "object" && error !== null && "status" in error && typeof error.status === "number"
      ? error.status
      : undefined;

  return status === undefined || (status >= SERVER_ERROR_STATUS && status !== SERVICE_UNAVAILABLE_STATUS);
}
