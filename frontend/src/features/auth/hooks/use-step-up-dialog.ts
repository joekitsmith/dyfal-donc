import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useSyncExternalStore } from "react";

import { apiClient } from "@/api/client";

import type { PasskeyFailure, SessionUser } from "../types";

import { signInWithPasskey } from "../api/passkey-ceremonies";
import { SESSION_QUERY_KEY } from "../constants";
import { cancelled, confirmed, isAwaitingConfirmation, subscribeToConfirmation } from "../stores/step-up-store";
import { passkeyFailure } from "../utils/passkey-failure";
import { replaceSession } from "../utils/replace-session";

/** The dialog that asks someone to confirm with their passkey before an account change goes ahead. */
export function useStepUpDialog() {
  const queryClient = useQueryClient();
  const open = useSyncExternalStore(subscribeToConfirmation, isAwaitingConfirmation, () => false);
  const confirm = useMutation({
    mutationFn: () => signInWithPasskey(apiClient),
    onSuccess: (user) => {
      const current = queryClient.getQueryData<null | SessionUser>(SESSION_QUERY_KEY);

      if (user.id === current?.id) {
        confirmed();
      } else {
        // A passkey for another account: that is who they are now, and the change is not made
        replaceSession(queryClient, user);
        cancelled();
      }
    },
  });
  const failure: null | PasskeyFailure = confirm.isError ? passkeyFailure(confirm.error) : null;

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
    failure,
    open,
  };
}
