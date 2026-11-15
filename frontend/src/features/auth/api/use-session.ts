import { useQuery } from "@tanstack/react-query";

import { apiClient } from "@/api/client";

import { SESSION_QUERY_KEY } from "../constants";
import { resolveSession } from "./auth-requests";

/** Who is signed in. Nobody signed in is an answer (null), not an error. */
export function useSession() {
  return useQuery({ queryFn: () => resolveSession(apiClient), queryKey: SESSION_QUERY_KEY });
}
