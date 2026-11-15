import { useMutation, useQueryClient } from "@tanstack/react-query";

import { apiClient } from "@/api/client";

import { RECOVERY_STATUS_QUERY_KEY } from "../constants";
import { showRecoveryCodes } from "../stores/recovery-codes-store";
import { replaceRecoveryCodes } from "./auth-requests";

export function useReplaceRecoveryCodes() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => replaceRecoveryCodes(apiClient),
    onSuccess: (codes) => {
      showRecoveryCodes(codes);
      void queryClient.invalidateQueries({ queryKey: RECOVERY_STATUS_QUERY_KEY });
    },
  });
}
