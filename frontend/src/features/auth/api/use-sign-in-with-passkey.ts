import { useMutation, useQueryClient } from "@tanstack/react-query";

import { apiClient } from "@/api/client";

import { replaceSession } from "../utils/replace-session";
import { signInWithPasskey } from "./passkey-ceremonies";

export function useSignInWithPasskey() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => signInWithPasskey(apiClient),
    onSuccess: (user) => {
      replaceSession(queryClient, user);
    },
  });
}
