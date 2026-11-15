import type { ApiClient } from "@/api/client";

import { unwrap } from "@/api/api-error";

import type { Overview, SessionSummary } from "../types";

export async function getOverview(client: ApiClient): Promise<Overview> {
  return unwrap(await client.GET("/me/overview"));
}

export async function getSessionSummary(client: ApiClient, sessionId: number): Promise<SessionSummary> {
  return unwrap(
    await client.GET("/me/learning-sessions/{session_id}/summary", { params: { path: { session_id: sessionId } } }),
  );
}
