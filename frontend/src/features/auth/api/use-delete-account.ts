import { useMutation, useQueryClient } from "@tanstack/react-query";

import { apiClient } from "@/api/client";

import { replaceSession } from "../utils/replace-session";
import { deleteAccount } from "./auth-requests";

export function useDeleteAccount() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => deleteAccount(apiClient),
    onSuccess: () => {
      replaceSession(queryClient, null);
    },
  });
}
