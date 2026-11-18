import { ApiError } from "@/api/api-error";
import { useRequireSession } from "@/features/auth";
import { useReportDialog } from "@/features/problem-report";
import { useReplayClip } from "@/hooks/use-replay-clip";

import { useItem } from "../api/use-item";
import { NOT_FOUND_STATUS } from "../constants";

/** What the item screen shows: the item once signed in, or that there is no such item, and how to hear it. */
export function useItemPage(itemId: string) {
  const { error: sessionError, user } = useRequireSession();
  const item = useItem(itemId);
  const { failed, play } = useReplayClip();
  const report = useReportDialog("item");
  const notFound = item.error instanceof ApiError && item.error.status === NOT_FOUND_STATUS;
  const audio = item.data?.audio;

  return {
    error: sessionError ?? (notFound ? null : item.error),
    isLoading: user === undefined || item.isPending,
    item: item.data,
    notFound,
    playback: {
      failed: failed !== null,
      play:
        audio === null || audio === undefined
          ? undefined
          : () => {
              play(audio);
            },
    },
    report,
  };
}
