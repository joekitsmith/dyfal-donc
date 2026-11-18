import { useQuery } from "@tanstack/react-query";

import { apiClient } from "@/api/client";

import { RECOVERY_STATUS_QUERY_KEY } from "../constants";
import { getRecoveryCodeStatus } from "./auth-requests";

/** How many recovery codes are unused. */
export function useRecoveryCodeStatus(enabled: boolean) {
  return useQuery({
    enabled,
    queryFn: () => getRecoveryCodeStatus(apiClient),
    queryKey: RECOVERY_STATUS_QUERY_KEY,
  });
}
