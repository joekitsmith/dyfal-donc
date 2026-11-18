import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useState, useSyncExternalStore } from "react";

import { apiClient } from "@/api/client";

import type { PasskeyFailure, SessionUser } from "../types";

import { signInWithPasskey } from "../api/passkey-ceremonies";
import { SESSION_QUERY_KEY, STEP_UP_FAILURES, STEP_UP_TEXT } from "../constants";
import {
  cancelled,
  confirmed,
  noteAccountSwitched,
  pendingAction,
  type StepUpAction,
  subscribeToConfirmation,
} from "../stores/step-up-store";
import { passkeyFailure } from "../utils/passkey-failure";
import { replaceSession } from "../utils/replace-session";

/** The dialog that asks someone to confirm with their passkey before an account change goes ahead. */
export function useStepUpDialog() {
  const queryClient = useQueryClient();
  const action = useSyncExternalStore(subscribeToConfirmation, pendingAction, () => null);
  // The dialog fades out after the action is gone, and should not lose its words while it does
  const [lastAction, setLastAction] = useState<StepUpAction>("add_passkey");
  const confirm = useMutation({
    mutationFn: () => signInWithPasskey(apiClient),
    onSuccess: (user) => {
      const current = queryClient.getQueryData<null | SessionUser>(SESSION_QUERY_KEY);

      if (user.id === current?.id) {
        confirmed();
      } else {
        // A passkey for another account: that is who they are now, and the change is not made
        replaceSession(queryClient, user);
        noteAccountSwitched();
        cancelled();
      }
    },
  });
  const failure: null | PasskeyFailure = confirm.isError ? passkeyFailure(confirm.error) : null;

  if (action !== null && action !== lastAction) {
    setLastAction(action);
  }

  return {
    cancel: () => {
      confirm.reset();
      cancelled();
    },
    confirm: {
      disabled: confirm.isPending,
      onClick: () => {
        confirm.mutate();
      },
    },
    failure: failure === null ? null : failureLine(failure),
    open: action !== null,
    text: STEP_UP_TEXT[action ?? lastAction],
  };
}

function failureLine(failure: PasskeyFailure): string {
  return failure === "cancelled" || failure === "not_recognised" ? STEP_UP_FAILURES[failure] : STEP_UP_FAILURES.other;
}
