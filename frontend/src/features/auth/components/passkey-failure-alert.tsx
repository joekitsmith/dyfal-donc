import Alert from "@mui/material/Alert";

import type { PasskeyFailure } from "../types";

import { FAILURE_MESSAGES } from "../constants";

export function PasskeyFailureAlert({ failure }: { readonly failure: PasskeyFailure }) {
  return <Alert severity={failure === "cancelled" ? "info" : "error"}>{FAILURE_MESSAGES[failure]}</Alert>;
}
