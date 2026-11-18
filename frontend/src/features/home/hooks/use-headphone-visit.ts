import { useEffect } from "react";

import { recordVisit } from "../stores/headphone-hint-store";

/** Counts one visit for as long as the component stays on screen, so stopping a lesson and starting another is still the same one. */
export function useHeadphoneVisit(): void {
  useEffect(() => {
    recordVisit();
  }, []);
}
