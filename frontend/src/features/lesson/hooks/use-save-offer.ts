import { useState } from "react";

import { useProgress } from "@/features/progress";

import { SAVE_OFFER_MINIMUM_ITEMS } from "../constants";

/**
 * When to suggest adding a passkey: to a guest, once they have learned enough to mind losing it.
 * Not now hides it until the next visit.
 */
export function useSaveOffer({ isGuest, learnerId }: { readonly isGuest: boolean; readonly learnerId: string }) {
  const { data } = useProgress(learnerId);
  const [dismissed, setDismissed] = useState(false);
  const [saved, setSaved] = useState(false);

  return {
    closeSaved: () => {
      setSaved(false);
    },
    dismiss: () => {
      setDismissed(true);
    },
    markSaved: () => {
      setSaved(true);
    },
    offered: isGuest && !dismissed && (data?.introduced ?? 0) >= SAVE_OFFER_MINIMUM_ITEMS,
    saved,
  };
}
