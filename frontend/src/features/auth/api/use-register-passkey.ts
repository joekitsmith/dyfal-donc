import { useMutation, useQueryClient } from "@tanstack/react-query";

import { apiClient } from "@/api/client";

import { PASSKEYS_QUERY_KEY, RECOVERY_STATUS_QUERY_KEY, SESSION_QUERY_KEY } from "../constants";
import { showRecoveryCodes } from "../stores/recovery-codes-store";
import { registerPasskey } from "./passkey-ceremonies";

export function useRegisterPasskey() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (label: string | undefined) => registerPasskey(apiClient, label),
    onSuccess: ({ recoveryCodes }) => {
      // Only the first passkey brings codes. They are shown once, wherever the passkey was added
      if (recoveryCodes !== null) {
        showRecoveryCodes(recoveryCodes);
      }

      void queryClient.invalidateQueries({ queryKey: RECOVERY_STATUS_QUERY_KEY });
      // The first passkey makes a guest an account, and the server has just given the browser a new cookie
      void queryClient.invalidateQueries({ queryKey: SESSION_QUERY_KEY });
      void queryClient.invalidateQueries({ queryKey: PASSKEYS_QUERY_KEY });
    },
  });
}
