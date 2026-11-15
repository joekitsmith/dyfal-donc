import Alert from "@mui/material/Alert";

import type { PasskeyFailure } from "../types";

import { FAILURE_MESSAGES } from "../constants";

type PasskeyFailureAlertProps = { readonly failure: PasskeyFailure };

export function PasskeyFailureAlert({ failure }: PasskeyFailureAlertProps) {
  return <Alert severity={failure === "cancelled" ? "info" : "error"}>{FAILURE_MESSAGES[failure]}</Alert>;
}
