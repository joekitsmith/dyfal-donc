import { useMutation, useQueryClient } from "@tanstack/react-query";

import { apiClient } from "@/api/client";

import type { UserSettings } from "../types";

import { SETTINGS_QUERY_KEY } from "../constants";
import { saveSettings } from "./settings-requests";

export function useSaveSettings() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (changes: Partial<UserSettings>) => saveSettings(apiClient, changes),
    onSuccess: (saved) => {
      queryClient.setQueryData(SETTINGS_QUERY_KEY, saved);
    },
  });
}
