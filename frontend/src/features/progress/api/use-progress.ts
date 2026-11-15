import { useQuery } from "@tanstack/react-query";

import { unwrap } from "@/api/api-error";
import { apiClient } from "@/api/client";

import { progressQueryKey } from "../constants";

export function useProgress(learnerId: string) {
  return useQuery({
    queryFn: async () =>
      unwrap(await apiClient.GET("/learners/{learner_id}/progress", { params: { path: { learner_id: learnerId } } })),
    queryKey: progressQueryKey(learnerId),
  });
}
