import { useMutation, useQueryClient } from "@tanstack/react-query";

import { apiClient } from "@/api/client";

import { replaceSession } from "../utils/replace-session";
import { signOut } from "./auth-requests";

export function useSignOut() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => signOut(apiClient),
    onSuccess: () => {
      replaceSession(queryClient, null);
    },
  });
}
