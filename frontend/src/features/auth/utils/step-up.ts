import { ApiError } from "@/api/api-error";

const FORBIDDEN_STATUS = 403;

/** The person chose not to confirm, so the change they asked for was not made. */
export class StepUpCancelledError extends Error {
  constructor() {
    super("Confirming with a passkey was cancelled");
  }
}

/** The server wants a sign-in just now before it changes the account. */
export function isStepUpRequired(error: unknown): boolean {
  return error instanceof ApiError && error.status === FORBIDDEN_STATUS;
}
