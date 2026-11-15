import { useMutation, useQueryClient } from "@tanstack/react-query";

import { apiClient } from "@/api/client";

import { PASSKEYS_QUERY_KEY } from "../constants";
import { removePasskey } from "./auth-requests";

export function useRemovePasskey() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (passkeyId: string) => removePasskey(apiClient, passkeyId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: PASSKEYS_QUERY_KEY }),
  });
}
