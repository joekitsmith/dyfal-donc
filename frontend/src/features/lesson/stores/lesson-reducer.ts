import type {
  ClipTrack,
  ExerciseFields,
  ExerciseState,
  LessonEvent,
  LessonExercise,
  LessonState,
  WaitingTrack,
} from "../types";

import { CLIP_ERROR_MESSAGE, NEXT_ERROR_MESSAGE, PLAYBACK_ERROR_MESSAGE, SUBMIT_ERROR_MESSAGE } from "../constants";

export const INITIAL_LESSON_STATE: LessonState = { phase: "idle" };

const ALL_LOADING: ExerciseFields["clips"] = { english: "loading", welsh: "loading", welsh_slow: "loading" };

const PAUSABLE_PHASES: ReadonlySet<LessonState["phase"]> = new Set([
  "awaiting_outcome",
  "playing_english",
  "playing_welsh",
  "playing_welsh_slow",
  "thinking",
  "waiting_for_clip",
]);

const PLAYING_PHASES: ReadonlySet<LessonState["phase"]> = new Set([
  "playing_english",
  "playing_welsh",
  "playing_welsh_slow",
]);

/** The lesson loop as a pure state machine. Audio, timers and requests live outside it. */
export function lessonReducer(state: LessonState, event: LessonEvent): LessonState {
  switch (event.type) {
    case "clip_ended":
      return clipEnded(state);
    case "clip_failed":
      return clipFailed(state, event.track);
    case "clip_ready":
      return clipReady(state, event.track);
    case "missed":
      return canMarkMissed(state) && isExerciseState(state) ? { ...state, missed: true } : state;
    case "next_failed":
      return state.phase === "loading"
        ? { message: NEXT_ERROR_MESSAGE, phase: "error", retry: { kind: "next" } }
        : state;
    case "next_loaded":
      return state.phase === "loading" ? prepare(event.exercise, 0, false) : state;
    case "nothing_eligible":
      return state.phase === "loading" ? { phase: "nothing_eligible", reason: event.reason } : state;
    case "playback_failed":
      return isExerciseState(state) && PLAYING_PHASES.has(state.phase) ? toClipError(state) : state;
    case "replay":
      return replay(state);
    case "reset":
      return INITIAL_LESSON_STATE;
    case "retry":
      return retry(state);
    case "skip_window":
    case "window_elapsed":
      return state.phase === "awaiting_outcome" && !state.paused ? { ...fieldsOf(state), phase: "submitting" } : state;
    case "start":
      return state.phase === "idle" || state.phase === "nothing_eligible" ? { phase: "loading" } : state;
    case "submit_failed":
      return state.phase === "submitting"
        ? {
            message: SUBMIT_ERROR_MESSAGE,
            phase: "error",
            retry: { attempt: state.attempt, exercise: state.exercise, kind: "submit", missed: state.missed },
          }
        : state;
    case "submitted":
      return state.phase === "submitting" ? { phase: "loading" } : state;
    case "think_elapsed":
      return state.phase === "thinking" && !state.paused ? startClip(state, "welsh") : state;
    case "toggle_pause":
      return togglePause(state);
    case "toggle_reveal":
      return isExerciseState(state) ? { ...state, revealed: !state.revealed } : state;
  }
}

/** "Missed it" counts from when the Welsh starts until the exercise advances. */
export function canMarkMissed(state: LessonState): boolean {
  switch (state.phase) {
    case "awaiting_outcome":
    case "playing_welsh":
    case "playing_welsh_slow":
      return true;
    case "waiting_for_clip":
      return state.track === "welsh_slow";
    default:
      return false;
  }
}

export function isExerciseState(state: LessonState): state is ExerciseState {
  return "exercise" in state;
}

export function isPausable(state: LessonState): boolean {
  return PAUSABLE_PHASES.has(state.phase);
}

function clipEnded(state: LessonState): LessonState {
  if (!isExerciseState(state) || state.paused) {
    return state;
  }

  switch (state.phase) {
    case "playing_english":
      return { ...fieldsOf(state), phase: "thinking" };
    case "playing_welsh":
      return startClip(state, "welsh_slow");
    case "playing_welsh_slow":
      return { ...fieldsOf(state), phase: "awaiting_outcome" };
    default:
      return state;
  }
}

function clipFailed(state: LessonState, track: ClipTrack): LessonState {
  if (!isExerciseState(state)) {
    return state;
  }

  const failed: ExerciseState = { ...state, clips: { ...state.clips, [track]: "failed" } };
  const neededNow =
    (state.phase === "preparing" && track === "english") ||
    (state.phase === "waiting_for_clip" && !state.paused && state.track === track);

  return neededNow ? toClipError(failed) : failed;
}

function clipReady(state: LessonState, track: ClipTrack): LessonState {
  if (!isExerciseState(state)) {
    return state;
  }

  const ready: ExerciseState = { ...state, clips: { ...state.clips, [track]: "ready" } };

  if (ready.phase === "preparing" && track === "english") {
    return { ...fieldsOf(ready), phase: "playing_english" };
  }

  if (ready.phase === "waiting_for_clip" && !ready.paused && ready.track === track) {
    return startClip(ready, ready.track);
  }

  return ready;
}

function fieldsOf(state: ExerciseState): ExerciseFields {
  const { attempt, clips, exercise, missed, paused, replayCount, revealed } = state;

  return { attempt, clips, exercise, missed, paused, replayCount, revealed };
}

function prepare(exercise: LessonExercise, attempt: number, missed: boolean): ExerciseState {
  return {
    attempt,
    clips: ALL_LOADING,
    exercise,
    missed,
    paused: false,
    phase: "preparing",
    replayCount: 0,
    revealed: false,
  };
}

function replay(state: LessonState): LessonState {
  if (!isExerciseState(state) || !PAUSABLE_PHASES.has(state.phase)) {
    return state;
  }

  return { ...fieldsOf(state), paused: false, phase: "playing_english", replayCount: state.replayCount + 1 };
}

function retry(state: LessonState): LessonState {
  if (state.phase !== "error") {
    return state;
  }

  const { retry: target } = state;

  if (target.kind === "next") {
    return { phase: "loading" };
  }

  if (target.kind === "clips") {
    return prepare(target.exercise, target.attempt + 1, target.missed);
  }

  return { ...fieldsOf(prepare(target.exercise, target.attempt, target.missed)), phase: "submitting" };
}

/** Plays the clip if it is ready, waits if it is still loading, and stops if it failed. */
function startClip(state: ExerciseState, track: WaitingTrack): LessonState {
  const fields = fieldsOf(state);

  switch (state.clips[track]) {
    case "failed":
      return toClipError(state);
    case "loading":
      return { ...fields, phase: "waiting_for_clip", track };
    case "ready":
      return track === "welsh" ? { ...fields, phase: "playing_welsh" } : { ...fields, phase: "playing_welsh_slow" };
  }
}

function toClipError(state: ExerciseState): LessonState {
  const loading = state.phase === "preparing" || state.phase === "waiting_for_clip";

  return {
    message: loading ? CLIP_ERROR_MESSAGE : PLAYBACK_ERROR_MESSAGE,
    phase: "error",
    retry: { attempt: state.attempt, exercise: state.exercise, kind: "clips", missed: state.missed },
  };
}

function togglePause(state: LessonState): LessonState {
  if (!isExerciseState(state) || !PAUSABLE_PHASES.has(state.phase)) {
    return state;
  }

  if (!state.paused) {
    return { ...state, paused: true };
  }

  const resumed: ExerciseState = { ...state, paused: false };

  return resumed.phase === "waiting_for_clip" ? startClip(resumed, resumed.track) : resumed;
}
