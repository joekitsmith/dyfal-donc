import { useMutation, useQueryClient } from "@tanstack/react-query";

import { apiClient } from "@/api/client";

import { replaceSession } from "../utils/replace-session";
import { startGuest } from "./auth-requests";

export function useStartGuest() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => startGuest(apiClient),
    onSuccess: (user) => {
      replaceSession(queryClient, user);
    },
  });
}
