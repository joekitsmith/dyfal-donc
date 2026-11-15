import { useEffect, useEffectEvent, useReducer, useRef, useState } from "react";

import { ApiError } from "@/api/api-error";

import type { ClipTrack, LessonState } from "../types";
import type { KeyAction } from "../utils/key-map";

import { useNextExercise } from "../api/use-next-exercise";
import { useSubmitOutcome } from "../api/use-submit-outcome";
import {
  ALREADY_ANSWERED_STATUS,
  BETWEEN_WELSH_MILLISECONDS,
  OUTCOME_WINDOW_MILLISECONDS,
  SELECTION_EXPIRED_STATUS,
} from "../constants";
import {
  canMarkMissed,
  INITIAL_LESSON_STATE,
  isExerciseState,
  isPausable,
  lessonReducer,
} from "../stores/lesson-reducer";
import { ClipPlayer } from "../utils/clip-player";
import { type PausableTimer, startPausableTimer } from "../utils/pausable-timer";
import { thinkSeconds } from "../utils/think-time";
import { useExerciseClips } from "./use-exercise-clips";
import { useLessonKeyboard } from "./use-lesson-keyboard";

const TRACK_FOR_PHASE: Readonly<Partial<Record<LessonState["phase"], ClipTrack>>> = {
  playing_english: "english",
  playing_welsh: "welsh",
  playing_welsh_slow: "welsh_slow",
};

const WAIT_FOR_PHASE: Readonly<
  Partial<
    Record<LessonState["phase"], { readonly event: "gap_elapsed" | "window_elapsed"; readonly milliseconds: number }>
  >
> = {
  awaiting_outcome: { event: "window_elapsed", milliseconds: OUTCOME_WINDOW_MILLISECONDS },
  between_welsh: { event: "gap_elapsed", milliseconds: BETWEEN_WELSH_MILLISECONDS },
};

const MILLISECONDS_PER_SECOND = 1000;

export type LessonActions = {
  readonly missed: () => void;
  readonly replay: () => void;
  readonly retry: () => void;
  readonly start: () => void;
  readonly togglePause: () => void;
};

/**
 * Runs the lesson: the reducer decides what happens next, and this hook does the things the
 * reducer can't (play audio, wait, call the API) and reports back what happened.
 */
export function useLessonPlayer({
  learnerId,
  thinkMultiplier,
}: {
  readonly learnerId: string;
  readonly thinkMultiplier: number;
}) {
  const [state, dispatch] = useReducer(lessonReducer, INITIAL_LESSON_STATE);
  const [player] = useState(() => new ClipPlayer());
  const { mutate: fetchNext } = useNextExercise(learnerId);
  const { mutate: submitOutcome } = useSubmitOutcome(learnerId);
  const timer = useRef<null | PausableTimer>(null);
  const marks = useRef({ loadingStartedAt: 0, thinkEndedAt: 0 });

  const exercise = isExerciseState(state) ? state.exercise : null;
  const attempt = isExerciseState(state) ? state.attempt : 0;
  const replayCount = isExerciseState(state) ? state.replayCount : 0;
  const paused = isExerciseState(state) && state.paused;
  const loadingRequest = state.phase === "loading" ? state : null;
  const submission = state.phase === "submitting" ? state : null;

  const urlFor = useExerciseClips(state.phase === "submitting" ? null : exercise, attempt, dispatch);

  const thinkMilliseconds = useEffectEvent(() =>
    exercise === null ? 0 : thinkSeconds(exercise.welsh, thinkMultiplier) * MILLISECONDS_PER_SECOND,
  );

  // Each request is made once, when its state is entered
  useEffect(() => {
    if (loadingRequest === null) {
      return;
    }

    marks.current.loadingStartedAt = performance.now();
    fetchNext(undefined, {
      onError: () => {
        dispatch({ type: "next_failed" });
      },
      onSuccess: (next) => {
        dispatch(
          next.kind === "exercise"
            ? { exercise: next.exercise, type: "next_loaded" }
            : { reason: next.reason, type: "nothing_eligible" },
        );
      },
    });
  }, [fetchNext, loadingRequest]);

  useEffect(() => {
    if (submission === null) {
      return;
    }

    submitOutcome(
      { outcome: submission.missed ? "missed_it" : "got_it", selectionId: submission.exercise.selectionId },
      {
        onError: (error) => {
          // Answered already, or too late: either way this exercise is finished
          const finished =
            error instanceof ApiError &&
            (error.status === ALREADY_ANSWERED_STATUS || error.status === SELECTION_EXPIRED_STATUS);

          dispatch({ type: finished ? "submitted" : "submit_failed" });
        },
        onSuccess: () => {
          dispatch({ type: "submitted" });
        },
      },
    );
  }, [submission, submitOutcome]);

  useEffect(() => {
    const track = TRACK_FOR_PHASE[state.phase];
    const url = track === undefined ? undefined : urlFor(track);

    if (track === undefined || url === undefined) {
      return;
    }

    player.play(url, {
      onEnded: () => {
        dispatch({ type: "clip_ended" });
      },
      onError: () => {
        dispatch({ type: "playback_failed" });
      },
      onStarted: () => {
        logLatency(state.phase, replayCount, marks.current);
      },
    });

    return () => {
      player.stop();
    };
  }, [exercise, player, replayCount, state.phase, urlFor]);

  useEffect(() => {
    const wait =
      state.phase === "thinking"
        ? { event: "think_elapsed" as const, milliseconds: thinkMilliseconds() }
        : WAIT_FOR_PHASE[state.phase];

    if (wait === undefined) {
      return;
    }

    const running = startPausableTimer(wait.milliseconds, () => {
      if (wait.event === "think_elapsed") {
        marks.current.thinkEndedAt = performance.now();
      }

      dispatch({ type: wait.event });
    });

    timer.current = running;

    return () => {
      running.cancel();
      timer.current = null;
    };
  }, [exercise, replayCount, state.phase]);

  useEffect(() => {
    if (paused) {
      player.pause();
      timer.current?.pause();
    } else {
      player.resume();
      timer.current?.resume();
    }
  }, [paused, player]);

  useEffect(
    () => () => {
      player.stop();
    },
    [player],
  );

  const actions: LessonActions = {
    missed: () => {
      dispatch({ type: "missed" });
    },
    replay: () => {
      dispatch({ type: "replay" });
    },
    retry: () => {
      dispatch({ type: "retry" });
    },
    start: () => {
      player.unlock();
      dispatch({ type: "start" });
    },
    togglePause: () => {
      dispatch({ type: "toggle_pause" });
    },
  };

  useLessonKeyboard((action: KeyAction) => {
    if (action === "toggle_pause" && (state.phase === "idle" || state.phase === "nothing_eligible")) {
      actions.start();
    } else {
      dispatch({ type: action });
    }
  });

  return { actions, canMiss: canMarkMissed(state), canPause: isPausable(state), state };
}

function logLatency(
  phase: LessonState["phase"],
  replayCount: number,
  marks: { loadingStartedAt: number; thinkEndedAt: number },
) {
  const now = performance.now();

  if (phase === "playing_english" && replayCount === 0 && marks.loadingStartedAt > 0) {
    console.info(`Time to first audio: ${(now - marks.loadingStartedAt).toFixed(0)} ms`);
    marks.loadingStartedAt = 0;
  }

  if (phase === "playing_welsh" && replayCount === 0 && marks.thinkEndedAt > 0) {
    console.info(`Welsh wait after think time: ${(now - marks.thinkEndedAt).toFixed(0)} ms`);
    marks.thinkEndedAt = 0;
  }
}
