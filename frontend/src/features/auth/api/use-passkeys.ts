import { useQuery } from "@tanstack/react-query";

import { apiClient } from "@/api/client";

import { PASSKEYS_QUERY_KEY } from "../constants";
import { listPasskeys } from "./auth-requests";

export function usePasskeys() {
  return useQuery({ queryFn: () => listPasskeys(apiClient), queryKey: PASSKEYS_QUERY_KEY });
}
