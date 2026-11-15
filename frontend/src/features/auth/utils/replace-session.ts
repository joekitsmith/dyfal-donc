import type { QueryClient } from "@tanstack/react-query";

import type { SessionUser } from "../types";

import { SESSION_QUERY_KEY } from "../constants";

/** Who is signed in changed, so nothing cached for the last person may be shown to the next. */
export function replaceSession(queryClient: QueryClient, user: null | SessionUser): void {
  queryClient.clear();
  queryClient.setQueryData(SESSION_QUERY_KEY, user);
}
