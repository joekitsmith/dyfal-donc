import { useMutation } from "@tanstack/react-query";

import type { components } from "@/api/schema";

import { apiClient } from "@/api/client";

import { sendProblemReport } from "./send-problem-report";

export function useSendProblemReport() {
  return useMutation({
    mutationFn: (body: components["schemas"]["ProblemReportRequest"]) => sendProblemReport(apiClient, body),
  });
}
