import { useState } from "react";

import { useProgress } from "@/features/progress";

import { SAVE_OFFER_MINIMUM_ITEMS } from "../constants";

type OfferState = {
  /** Not now lasts until the page is opened again. */
  readonly dismissed: boolean;
  /** The exercise the offer was last decided for. */
  readonly exercise: null | string;
  readonly offered: boolean;
  readonly saved: boolean;
};

/**
 * When to suggest adding a passkey: to a guest, once they have learned enough to mind losing it.
 * The suggestion is decided when an exercise begins and not while one is under way, so nothing
 * appears in the middle of a sentence. Once shown it stays until it is dismissed, and the
 * confirmation that follows a passkey stays until the next exercise begins.
 *
 * `exercise` names the exercise being shown, or is null when there is none, as at rest.
 */
export function useSaveOffer({
  exercise,
  isGuest,
  learnerId,
}: {
  readonly exercise: null | string;
  readonly isGuest: boolean;
  readonly learnerId: string;
}) {
  const { data } = useProgress(learnerId);
  const [state, setState] = useState<OfferState>({ dismissed: false, exercise: null, offered: false, saved: false });
  const eligible = isGuest && !state.dismissed && (data?.introduced ?? 0) >= SAVE_OFFER_MINIMUM_ITEMS;

  if (exercise !== null && exercise !== state.exercise) {
    setState({ ...state, exercise, offered: eligible, saved: false });
  }

  return {
    confirmation: { visible: state.saved },
    prompt: {
      onDismiss: () => {
        setState((previous) => ({ ...previous, dismissed: true, offered: false }));
      },
      onSaved: () => {
        setState((previous) => ({ ...previous, offered: false, saved: true }));
      },
      visible: state.offered,
    },
  };
}
