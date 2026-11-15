import type { ApiClient } from "@/api/client";
import type { components } from "@/api/schema";

import { assertOk } from "@/api/api-error";

export async function sendProblemReport(
  client: ApiClient,
  body: components["schemas"]["ProblemReportRequest"],
): Promise<void> {
  assertOk(await client.POST("/me/problem-reports", { body }));
}
