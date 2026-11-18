import { useEffect, useState } from "react";

import type { RunningLessonState } from "../types";
import type { LessonView } from "../utils/lesson-view";

import { HANDOVER_VISIBLE_MILLISECONDS } from "../constants";
import { lessonView } from "../utils/lesson-view";

/** What the lesson screen shows, which also depends on how long the handover to the next exercise has taken. */
export function useLessonView(state: RunningLessonState): LessonView {
  const handover = handoverOf(state);
  const [waitedFor, setWaitedFor] = useState<null | string>(null);

  useEffect(() => {
    if (handover === null) {
      return;
    }

    const timer = setTimeout(() => {
      setWaitedFor(handover);
    }, HANDOVER_VISIBLE_MILLISECONDS);

    return () => {
      clearTimeout(timer);
    };
  }, [handover]);

  return lessonView(state, handover !== null && waitedFor === handover);
}

/** Names the handover that follows an exercise, so that a wait is never carried over to the next one. */
function handoverOf(state: RunningLessonState): null | string {
  if (state.phase === "submitting") {
    return state.exercise.selectionId;
  }

  return state.phase === "loading" && state.previous !== undefined ? state.previous.exercise.selectionId : null;
}
