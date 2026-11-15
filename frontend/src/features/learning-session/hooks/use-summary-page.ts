import { ApiError } from "@/api/api-error";
import { useRequireSession } from "@/features/auth";
import { useReportDialog } from "@/features/problem-report";

import { useSessionSummary } from "../api/use-session-summary";
import { NOT_FOUND_STATUS } from "../constants";

/** What the summary screen shows: the session's summary once signed in, or that there is no such session. */
export function useSummaryPage(sessionId: number) {
  const { error: sessionError, user } = useRequireSession();
  const summary = useSessionSummary(sessionId);
  const report = useReportDialog("summary");
  const notFound = summary.error instanceof ApiError && summary.error.status === NOT_FOUND_STATUS;

  return {
    error: sessionError ?? (notFound ? null : summary.error),
    isLoading: user === undefined || summary.isPending,
    notFound,
    report,
    summary: summary.data,
  };
}
