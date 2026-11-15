import { useQuery } from "@tanstack/react-query";

import { apiClient } from "@/api/client";

import { OVERVIEW_QUERY_KEY } from "../constants";
import { getOverview } from "./learning-session-requests";

/** What the home screen shows. It is read again whenever a screen needs it, because time passing changes it. */
export function useOverview() {
  return useQuery({
    queryFn: () => getOverview(apiClient),
    queryKey: OVERVIEW_QUERY_KEY,
    refetchOnMount: "always",
  });
}
