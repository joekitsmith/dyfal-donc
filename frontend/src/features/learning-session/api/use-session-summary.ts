import { useQuery } from "@tanstack/react-query";

import { apiClient } from "@/api/client";

import { summaryQueryKey } from "../constants";
import { getSessionSummary } from "./learning-session-requests";

export function useSessionSummary(sessionId: number) {
  return useQuery({
    queryFn: () => getSessionSummary(apiClient, sessionId),
    queryKey: summaryQueryKey(sessionId),
    refetchOnMount: "always",
  });
}
