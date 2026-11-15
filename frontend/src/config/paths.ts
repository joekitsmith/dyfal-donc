export const API_BASE_PATH = "/api";

export const ROUTES = {
  account: "/account",
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
