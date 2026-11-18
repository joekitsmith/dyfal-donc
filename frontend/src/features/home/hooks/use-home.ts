import { useRequireSession } from "@/features/auth";
import { useOverview } from "@/features/learning-session";

import type { HomeCardsContent } from "../types";

import { useHeadphoneHint } from "./use-headphone-hint";

/** What the home screen shows: the cards for what has happened so far, and what the start button says. */
export function useHome() {
  const { error: sessionError, user } = useRequireSession();
  const overview = useOverview();
  const headphoneHint = useHeadphoneHint();
  const recap = overview.data?.latest_session ?? null;
  const guest = user?.isGuest === true && recap !== null;

  const cards: HomeCardsContent = {
    error:
      sessionError !== null || overview.isError
        ? {
            retry: () => {
              void overview.refetch();
            },
          }
        : null,
    everythingMet: recap !== null && overview.data?.new_words_ready === false,
    guest,
    howItGoes: overview.data !== undefined && recap === null,
    recap,
  };

  return {
    cards,
    // The guest card says it all, so the hint waits
    hint: { visible: headphoneHint && !guest },
    isLoading: user === undefined || overview.isPending,
    slab: { brandNew: cards.howItGoes },
  };
}
