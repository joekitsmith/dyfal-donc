import type { FailureCause } from "../types";

import { LESSON_ERRORS } from "../constants";

/** What to tell the learner when something failed: the cause if it is known, otherwise what was being done. */
export function lessonError(
  context: "clips" | "next" | "playback" | "submit",
  cause: FailureCause,
): { readonly text: string; readonly title: string } {
  return LESSON_ERRORS[cause === "other" ? context : cause];
}
