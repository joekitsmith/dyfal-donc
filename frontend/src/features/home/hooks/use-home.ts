import { useRequireSession } from "@/features/auth";
import { useOverview } from "@/features/learning-session";
import { useReportDialog } from "@/features/problem-report";

/** What the home screen shows: who is signed in, and the overview of their learning. */
export function useHome() {
  const { error: sessionError, user } = useRequireSession();
  const overview = useOverview();
  const report = useReportDialog("general");

  return {
    error: sessionError ?? overview.error,
    isLoading: user === undefined || overview.isPending,
    overview: overview.data,
    report,
    user,
  };
}
