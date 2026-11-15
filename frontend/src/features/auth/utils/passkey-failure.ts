import { WebAuthnError } from "@simplewebauthn/browser";

import { ApiError } from "@/api/api-error";

import type { PasskeyFailure } from "../types";

import { BAD_REQUEST_STATUS, CONFLICT_STATUS } from "../constants";
import { StepUpCancelledError } from "./step-up";

/** Why a passkey ceremony failed, from what the browser or the server said. */
export function passkeyFailure(error: unknown): PasskeyFailure {
  if (error instanceof StepUpCancelledError) {
    return "cancelled";
  }

  if (error instanceof WebAuthnError) {
    return webAuthnFailure(error);
  }

  if (error instanceof ApiError) {
    if (error.status === CONFLICT_STATUS) {
      return "already_registered";
    }

    if (error.status === BAD_REQUEST_STATUS) {
      return "not_recognised";
    }
  }

  return "other";
}

function webAuthnFailure(error: WebAuthnError): PasskeyFailure {
  if (error.code === "ERROR_AUTHENTICATOR_PREVIOUSLY_REGISTERED") {
    return "already_registered";
  }

  // The browser reports a dismissed prompt as NotAllowedError, which the library passes through
  const dismissed = error.cause instanceof Error && error.cause.name === "NotAllowedError";

  return dismissed || error.code === "ERROR_CEREMONY_ABORTED" ? "cancelled" : "other";
}
