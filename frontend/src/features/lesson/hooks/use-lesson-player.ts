import { useQueryClient } from "@tanstack/react-query";
import { useEffect, useEffectEvent, useReducer, useRef, useState } from "react";

import { ApiError } from "@/api/api-error";
import { replaceSession } from "@/features/auth";
import { OVERVIEW_QUERY_KEY } from "@/features/learning-session";
import { progressQueryKey } from "@/features/progress";

import type { LessonExercise, LessonSettings, Timeline } from "../types";
import type { KeyAction } from "../utils/key-map";

import { useNextExercise } from "../api/use-next-exercise";
import { useSubmitOutcome } from "../api/use-submit-outcome";
import { ALREADY_ANSWERED_STATUS, DEFAULT_WELSH_PLAYBACK, SELECTION_EXPIRED_STATUS } from "../constants";
import {
  canMarkMissed,
  INITIAL_LESSON_STATE,
  isExerciseState,
  isPausable,
  lessonReducer,
} from "../stores/lesson-reducer";
import { type ThinkWindow, thinkWindow } from "../utils/beats";
import { failureCause } from "../utils/failure-cause";
import { isSignedOut } from "../utils/is-signed-out";
import { rememberExercise } from "../utils/remember-exercise";
import { TrackPlayer } from "../utils/track-player";
import { useExerciseTrack } from "./use-exercise-track";
import { useLessonKeyboard } from "./use-lesson-keyboard";
import { useLessonMediaSession } from "./use-lesson-media-session";
import { useTrackPosition } from "./use-track-position";

export type LessonActions = {
  readonly missed: () => void;
  /** Pauses the lesson if it is not paused already, unlike ``togglePause``. */
  readonly pause: () => void;
  readonly replay: () => void;
  readonly resume: () => void;
  readonly retry: () => void;
  /** Ends the outcome window early. */
  readonly skipWindow: () => void;
  readonly start: () => void;
  /** Ends the lesson and returns to rest, dropping the exercise that was playing. */
  readonly stop: () => void;
  readonly togglePause: () => void;
};

/**
 * Runs the lesson: the reducer decides what happens next, and this hook does the things the
 * reducer can't (play audio, call the API) and reports back what happened. Each exercise is one
 * track of audio, so where the audio is says which phase the lesson is in.
 */
export function useLessonPlayer({
  learnerId,
  settings,
}: {
  readonly learnerId: string;
  readonly settings: LessonSettings;
}) {
  const [state, dispatch] = useReducer(lessonReducer, INITIAL_LESSON_STATE);
  const [player] = useState(() => new TrackPlayer());
  const [recent, setRecent] = useState<readonly LessonExercise[]>([]);
  const { mutate: fetchNext, reset: forgetNext } = useNextExercise();
  const { mutate: submitOutcome } = useSubmitOutcome();
  const queryClient = useQueryClient();
  const timeline = useRef<null | Timeline>(null);

  const exercise = isExerciseState(state) ? state.exercise : null;
  const attempt = isExerciseState(state) ? state.attempt : 0;
  const paused = isExerciseState(state) && state.paused;
  const welshPlayback = isExerciseState(state) ? state.welshPlayback : DEFAULT_WELSH_PLAYBACK;
  const loadingRequest = state.phase === "loading" ? state : null;
  const submission = state.phase === "submitting" ? state : null;
  const canPause = isPausable(state);

  const refreshProgress = useEffectEvent(() => {
    void queryClient.invalidateQueries({ queryKey: progressQueryKey(learnerId) });
    // The session clock and the recap on the home screen come from the overview
    void queryClient.invalidateQueries({ queryKey: OVERVIEW_QUERY_KEY });
  });

  // The screen watching the session then sends the person to the welcome screen
  const endSession = useEffectEvent(() => {
    replaceSession(queryClient, null);
  });

  const welshPlaybackSetting = useEffectEvent(() => settings.welshPlayback);

  useExerciseTrack({
    attempt,
    dispatch,
    exercise: state.phase === "submitting" ? null : exercise,
    player,
    settings,
    timelineRef: timeline,
    welshPlayback,
  });
  useTrackPosition({ canPause, dispatch, player, timelineRef: timeline });

  // Each request is made once, when its state is entered
  useEffect(() => {
    if (loadingRequest === null) {
      return;
    }

    fetchNext(undefined, {
      onError: (error) => {
        if (isSignedOut(error)) {
          endSession();
        } else {
          dispatch({ cause: failureCause(error), type: "next_failed" });
        }
      },
      onSuccess: (next) => {
        if (next.kind === "exercise") {
          setRecent((previous) => rememberExercise(previous, next.exercise));
        }

        dispatch(
          next.kind === "exercise"
            ? { exercise: next.exercise, type: "next_loaded", welshPlayback: welshPlaybackSetting() }
            : { type: "nothing_eligible" },
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
          if (isSignedOut(error)) {
            endSession();

            return;
          }

          // Answered already, or too late: either way this exercise is finished
          const finished =
            error instanceof ApiError &&
            (error.status === ALREADY_ANSWERED_STATUS || error.status === SELECTION_EXPIRED_STATUS);

          if (finished) {
            refreshProgress();
            dispatch({ type: "submitted" });
          } else {
            dispatch({ cause: failureCause(error), type: "submit_failed" });
          }
        },
        onSuccess: () => {
          refreshProgress();
          dispatch({ type: "submitted" });
        },
      },
    );
  }, [submission, submitOutcome]);

  useEffect(() => {
    if (paused) {
      player.pause();
    } else {
      player.resume();
    }
  }, [paused, player]);

  // The lock screen then shows paused, and the error is there when the screen is next seen
  useEffect(() => {
    if (state.phase === "error") {
      player.pause();
    }
  }, [player, state.phase]);

  useEffect(
    () => () => {
      player.stop();
    },
    [player],
  );

  // The audio is controlled here as well as through the state, because the lock screen's buttons
  // must act at once, and the state is only a render away
  const actions: LessonActions = {
    missed: () => {
      dispatch({ type: "missed" });
    },
    pause: () => {
      if (canPause && !paused) {
        player.pause();
        dispatch({ type: "pause" });
      }
    },
    replay: () => {
      if (canPause) {
        player.seekToStart();
        dispatch({ type: "replay" });
      }
    },
    resume: () => {
      if (canPause && paused) {
        player.resume();
        dispatch({ type: "resume" });
      }
    },
    retry: () => {
      dispatch({ type: "retry" });
    },
    skipWindow: () => {
      dispatch({ type: "skip_window" });
    },
    start: () => {
      player.unlock();
      dispatch({ type: "start" });
    },
    stop: () => {
      player.stop();
      // So an exercise still being fetched cannot be remembered for a report
      forgetNext();
      dispatch({ type: "reset" });
    },
    togglePause: () => {
      if (paused) {
        actions.resume();
      } else {
        actions.pause();
      }
    },
  };

  useLessonMediaSession({
    actions,
    active: state.phase !== "idle",
    english: exercise !== null && state.phase !== "preparing" ? exercise.english : null,
    paused,
  });

  useLessonKeyboard((action: KeyAction) => {
    switch (action) {
      case "missed":
        actions.missed();
        break;
      case "replay":
        actions.replay();
        break;
      case "skip_window":
        actions.skipWindow();
        break;
      case "toggle_pause":
        if (state.phase === "idle") {
          actions.start();
        } else {
          actions.togglePause();
        }

        break;
    }
  });

  // For the beat row, which reads it on each frame rather than rendering on each change of position
  const readThink = (): null | ThinkWindow =>
    timeline.current === null ? null : thinkWindow(timeline.current, player.position);

  return { actions, canMiss: canMarkMissed(state), canPause, readThink, recent, state };
}
