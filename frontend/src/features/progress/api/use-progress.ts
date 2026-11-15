import { useQuery } from "@tanstack/react-query";

import { unwrap } from "@/api/api-error";
import { apiClient } from "@/api/client";

import { progressQueryKey } from "../constants";

export function useProgress(learnerId: string) {
  return useQuery({
    queryFn: async () => unwrap(await apiClient.GET("/me/progress")),
    queryKey: progressQueryKey(learnerId),
  });
}
