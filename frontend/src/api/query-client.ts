import { QueryClient } from "@tanstack/react-query";

/**
 * Nothing refetches by itself. Asking for the next exercise issues a selection on the server,
 * so a refetch on window focus or a retry would leave selections nobody answers.
 */
export function createQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      mutations: { retry: false },
      queries: {
        refetchOnReconnect: false,
        refetchOnWindowFocus: false,
        retry: false,
        staleTime: Infinity,
      },
    },
  });
}
