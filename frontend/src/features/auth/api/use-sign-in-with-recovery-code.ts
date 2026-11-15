import { useMutation, useQueryClient } from "@tanstack/react-query";

import { apiClient } from "@/api/client";

import { replaceSession } from "../utils/replace-session";
import { signInWithRecoveryCode } from "./auth-requests";

export function useSignInWithRecoveryCode() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (code: string) => signInWithRecoveryCode(apiClient, code),
    onSuccess: (user) => {
      replaceSession(queryClient, user);
    },
  });
}
