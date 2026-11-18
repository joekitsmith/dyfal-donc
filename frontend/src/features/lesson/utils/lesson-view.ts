import type { ExerciseState, LessonExercise, LessonState } from "../types";

import { LESSON_ERRORS } from "../constants";
import { canMarkMissed } from "../stores/lesson-reducer";
import { beatCount } from "./beats";

type BeatMode = "all-done" | "all-to-come" | "first-now" | "opened";

/** What each part of the lesson screen shows for a state. The screen itself only draws this. */
export type LessonView = {
  readonly beats: { readonly count: number; readonly mode: BeatMode };
  /** Shown where the Welsh will be, or under it once it has appeared. */
  readonly caption: null | string;
  readonly controls: { readonly look: "normal" | "unavailable"; readonly pause: "pause" | "resume" };
  readonly english: string;
  readonly error: LessonViewError | null;
  /** Whether the button that ends the outcome window early is there. */
  readonly next: boolean;
  readonly paused: boolean;
  readonly slab: "available" | "marked" | "waiting";
  readonly welsh: string;
};

type LessonViewError = {
  readonly action: "account" | "retry" | null;
  readonly text: string;
  readonly title: string;
};

type RunningState = Exclude<LessonState, { readonly phase: "idle" }>;

const RESTING_BEAT_COUNT = 8;
const NEW_ITEM_CAPTION = "Something new. Have a guess.";

const WAITING: LessonView = {
  beats: { count: RESTING_BEAT_COUNT, mode: "first-now" },
  caption: null,
  controls: { look: "unavailable", pause: "pause" },
  english: "",
  error: null,
  next: false,
  paused: false,
  slab: "waiting",
  welsh: "",
};

/**
 * `waitedLong` says the handover to the next exercise has taken longer than it is hidden for. The
 * lesson cannot know that from its state alone, because it is about time.
 */
export function lessonView(state: RunningState, waitedLong: boolean): LessonView {
  switch (state.phase) {
    case "error":
      return errorView(state);
    case "loading":
      return loadingView(state, waitedLong);
    case "nothing_eligible":
      return {
        ...WAITING,
        beats: { count: RESTING_BEAT_COUNT, mode: "all-to-come" },
        error: { action: null, ...LESSON_ERRORS.nothing_eligible },
      };
    default:
      return exerciseView(state);
  }
}

function captionFor(state: ExerciseState): string {
  const { exercise, revealed, welshPlayback } = state;
  const english = exercise.introducesItem ? NEW_ITEM_CAPTION : "Listen";
  const thinking = exercise.introducesItem ? NEW_ITEM_CAPTION : "Say it in Welsh";

  switch (state.phase) {
    case "awaiting_outcome":
    case "submitting":
      return "Next one coming up";
    case "between_welsh":
      return "Now listen";
    case "playing_welsh_slow":
      return welshPlayback === "both" ? "Once more, slowly" : "Listen";
    case "playing_welsh_standard":
      return revealed && welshPlayback === "standard" ? "Listen" : "Now listen";
    case "thinking":
      return thinking;
    default:
      return english;
  }
}

function errorView(state: Extract<LessonState, { readonly phase: "error" }>): LessonView {
  const { retry } = state;
  const exercise: LessonExercise | null = retry.kind === "next" ? null : retry.exercise;
  const noProgress = state.cause === "learner_missing";

  return {
    ...WAITING,
    beats: { count: exercise === null ? RESTING_BEAT_COUNT : beatCount(exercise.welsh), mode: "all-to-come" },
    english: exercise === null || noProgress ? "" : exercise.english,
    error: { action: noProgress ? "account" : "retry", text: state.text, title: state.title },
  };
}

function exerciseView(state: ExerciseState): LessonView {
  const { exercise, paused, revealed } = state;
  const count = beatCount(exercise.welsh);

  if (state.phase === "preparing" && state.isFirst) {
    return {
      ...WAITING,
      beats: { count, mode: "first-now" },
      caption: "Getting the first one…",
      english: exercise.english,
    };
  }

  return {
    beats: { count, mode: beatMode(state) },
    caption: paused ? "Paused" : captionFor(state),
    controls: { look: "normal", pause: paused ? "resume" : "pause" },
    english: exercise.english,
    error: null,
    next: state.phase === "awaiting_outcome" && !paused,
    paused,
    slab: slabFor(state),
    welsh: revealed ? exercise.welsh : "",
  };
}

function beatMode(state: ExerciseState): BeatMode {
  if (state.revealed) {
    return "opened";
  }

  switch (state.phase) {
    case "playing_english":
    case "preparing":
    case "thinking":
      return "all-to-come";
    default:
      return "all-done";
  }
}

function loadingView(state: Extract<LessonState, { readonly phase: "loading" }>, waitedLong: boolean): LessonView {
  if (state.previous === undefined) {
    return { ...WAITING, caption: "Getting the first one…" };
  }

  if (waitedLong) {
    return { ...WAITING, caption: "Getting the next one…" };
  }

  return exerciseView({ ...state.previous, phase: "submitting" });
}

function slabFor(state: ExerciseState): LessonView["slab"] {
  if (state.missed) {
    return "marked";
  }

  return canMarkMissed(state) || state.phase === "submitting" ? "available" : "waiting";
}
