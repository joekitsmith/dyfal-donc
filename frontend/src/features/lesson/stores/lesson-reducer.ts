import type {
  ExerciseFields,
  ExerciseState,
  FailureCause,
  LessonEvent,
  LessonExercise,
  LessonState,
  PositionPhase,
  WelshPlayback,
} from "../types";

import { errorMessage } from "../utils/error-message";

export const INITIAL_LESSON_STATE: LessonState = { phase: "idle" };

/** The order a track plays its phases in. The position only ever moves the lesson forward through it. */
const TRACK_PHASES: readonly PositionPhase[] = [
  "playing_english",
  "thinking",
  "playing_welsh_standard",
  "between_welsh",
  "playing_welsh_slow",
  "awaiting_outcome",
  "submitting",
];

const PAUSABLE_PHASES: ReadonlySet<LessonState["phase"]> = new Set([
  "awaiting_outcome",
  "between_welsh",
  "playing_english",
  "playing_welsh_slow",
  "playing_welsh_standard",
  "thinking",
]);

/** The lesson loop as a pure state machine. Audio, requests and the clock of the track live outside it. */
export function lessonReducer(state: LessonState, event: LessonEvent): LessonState {
  switch (event.type) {
    case "missed":
      return canMarkMissed(state) && isExerciseState(state) ? { ...state, missed: true } : state;
    case "next_failed":
      return state.phase === "loading"
        ? { cause: event.cause, message: errorMessage("next", event.cause), phase: "error", retry: { kind: "next" } }
        : state;
    case "next_loaded":
      return state.phase === "loading" ? prepare(event.exercise, 0, false, event.welshPlayback) : state;
    case "nothing_eligible":
      return state.phase === "loading" ? { phase: "nothing_eligible" } : state;
    case "pause":
      return setPaused(state, true);
    case "playback_failed":
      return isExerciseState(state) && PAUSABLE_PHASES.has(state.phase) ? toClipError(state, "other") : state;
    case "position_reached":
      return positionReached(state, event.phase);
    case "replay":
      return replay(state);
    case "reset":
      return INITIAL_LESSON_STATE;
    case "resume":
      return setPaused(state, false);
    case "retry":
      return retry(state);
    case "skip_window":
      return state.phase === "awaiting_outcome" && !state.paused ? { ...fieldsOf(state), phase: "submitting" } : state;
    case "start":
      return state.phase === "idle" ? { phase: "loading" } : state;
    case "submit_failed":
      return state.phase === "submitting"
        ? {
            cause: event.cause,
            message: errorMessage("submit", event.cause),
            phase: "error",
            retry: {
              attempt: state.attempt,
              exercise: state.exercise,
              kind: "submit",
              missed: state.missed,
              welshPlayback: state.welshPlayback,
            },
          }
        : state;
    case "submitted":
      return state.phase === "submitting" ? { phase: "loading" } : state;
    case "toggle_pause":
      return isExerciseState(state) ? setPaused(state, !state.paused) : state;
    case "track_failed":
      return state.phase === "preparing" ? toClipError(state, event.cause) : state;
    case "track_ready":
      return state.phase === "preparing" ? { ...fieldsOf(state), phase: "playing_english" } : state;
  }
}

/** "Missed it" counts from when the Welsh starts until the exercise advances. */
export function canMarkMissed(state: LessonState): boolean {
  switch (state.phase) {
    case "awaiting_outcome":
    case "between_welsh":
    case "playing_welsh_slow":
    case "playing_welsh_standard":
      return true;
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

function fieldsOf(state: ExerciseState): ExerciseFields {
  const { attempt, exercise, missed, paused, replayCount, revealed, welshPlayback } = state;

  return { attempt, exercise, missed, paused, replayCount, revealed, welshPlayback };
}

function prepare(
  exercise: LessonExercise,
  attempt: number,
  missed: boolean,
  welshPlayback: WelshPlayback,
): ExerciseState {
  return {
    attempt,
    exercise,
    missed,
    paused: false,
    phase: "preparing",
    replayCount: 0,
    revealed: false,
    welshPlayback,
  };
}

/**
 * Moves forward to the phase the track has reached, which may skip some when the page was not
 * running for a while. It is ignored while paused, and when it would move back: a replay is
 * what moves back.
 */
function positionReached(state: LessonState, phase: PositionPhase): LessonState {
  if (!isExerciseState(state) || state.paused) {
    return state;
  }

  const current = TRACK_PHASES.indexOf(state.phase as PositionPhase);
  const reached = TRACK_PHASES.indexOf(phase);

  if (current === -1 || reached <= current) {
    return state;
  }

  return {
    ...fieldsOf(state),
    phase,
    revealed: state.revealed || reached >= TRACK_PHASES.indexOf(firstWelshShown(state.welshPlayback)),
  };
}

/**
 * The text shows when a recording starts that nothing else follows, so with both voices it waits
 * for the man.
 */
function firstWelshShown(welshPlayback: WelshPlayback): PositionPhase {
  return welshPlayback === "standard" ? "playing_welsh_standard" : "playing_welsh_slow";
}

function replay(state: LessonState): LessonState {
  if (!isExerciseState(state) || !PAUSABLE_PHASES.has(state.phase)) {
    return state;
  }

  return {
    ...fieldsOf(state),
    paused: false,
    phase: "playing_english",
    replayCount: state.replayCount + 1,
  };
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
    return prepare(target.exercise, target.attempt + 1, target.missed, target.welshPlayback);
  }

  return {
    ...fieldsOf(prepare(target.exercise, target.attempt, target.missed, target.welshPlayback)),
    phase: "submitting",
  };
}

function setPaused(state: LessonState, paused: boolean): LessonState {
  if (!isExerciseState(state) || !PAUSABLE_PHASES.has(state.phase) || state.paused === paused) {
    return state;
  }

  return { ...state, paused };
}

function toClipError(state: ExerciseState, cause: FailureCause): LessonState {
  return {
    cause,
    message: errorMessage(state.phase === "preparing" ? "clips" : "playback", cause),
    phase: "error",
    retry: {
      attempt: state.attempt,
      exercise: state.exercise,
      kind: "clips",
      missed: state.missed,
      welshPlayback: state.welshPlayback,
    },
  };
}
