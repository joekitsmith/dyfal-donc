export const OVERVIEW_QUERY_KEY = ["overview"] as const;

export function summaryQueryKey(sessionId: number) {
  return ["learning-session-summary", sessionId] as const;
}

export const SECONDS_PER_MINUTE = 60;

export const NOT_FOUND_STATUS = 404;
