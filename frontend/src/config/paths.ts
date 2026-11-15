export const API_BASE_PATH = "/api";

export const ROUTES = {
  account: "/account",
  course: "/course",
  home: "/",
  learn: "/learn",
  recover: "/recover",
  settings: "/settings",
  welcome: "/welcome",
} as const;

/** The summary screen for one learning session. */
export function learningSessionPath(sessionId: number) {
  return `/learning-sessions/${sessionId}` as const;
}

/** The screen for one word or phrase the learner has met. */
export function courseItemPath(itemId: string) {
  return `/course/items/${encodeURIComponent(itemId)}` as const;
}
