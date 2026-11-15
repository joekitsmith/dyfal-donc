import type { CLIP_TRACKS } from "./constants";

type ClipLinks = Readonly<Record<ClipTrack, string>>;

export type ClipTrack = (typeof CLIP_TRACKS)[number];

export type ExerciseFields = {
  /** Counts retries of the clips, so a retry fetches them again. */
  readonly attempt: number;
  readonly exercise: LessonExercise;
  readonly missed: boolean;
  readonly paused: boolean;
  /** Counts replays, so a replay starts the English again even when it is already playing. */
  readonly replayCount: number;
  readonly revealed: boolean;
  /** Which Welsh recordings this exercise plays. Fixed when it is loaded. */
  readonly welshPlayback: WelshPlayback;
};

export type FailureCause = "learner_missing" | "other" | "speech_unavailable";

export type ExerciseState = Extract<LessonState, { readonly exercise: LessonExercise }>;

export type LessonEvent =
  | { readonly cause: FailureCause; readonly type: "next_failed" | "submit_failed" | "track_failed" }
  | { readonly exercise: LessonExercise; readonly type: "next_loaded"; readonly welshPlayback: WelshPlayback }
  | { readonly phase: PositionPhase; readonly type: "position_reached" }
  | {
      readonly type:
        | "missed"
        | "nothing_eligible"
        | "pause"
        | "playback_failed"
        | "replay"
        | "reset"
        | "resume"
        | "retry"
        | "skip_window"
        | "start"
        | "submitted"
        | "toggle_pause"
        | "track_ready";
    };

export type LessonExercise = {
  readonly audio: ClipLinks;
  readonly english: string;
  /** The exercise itself, which a problem report names. ``selectionId`` is this one time it was given. */
  readonly exerciseId: string;
  readonly selectionId: string;
  readonly welsh: string;
};

/** The settings the lesson uses. They are read when each exercise is loaded. */
export type LessonSettings = {
  readonly thinkTimeMultiplier: number;
  readonly welshPlayback: WelshPlayback;
};

export type LessonState =
  | (ExerciseFields & { readonly phase: "awaiting_outcome" })
  | (ExerciseFields & { readonly phase: "between_welsh" })
  | (ExerciseFields & { readonly phase: "playing_english" })
  | (ExerciseFields & { readonly phase: "playing_welsh_slow" })
  | (ExerciseFields & { readonly phase: "playing_welsh_standard" })
  | (ExerciseFields & { readonly phase: "preparing" })
  | (ExerciseFields & { readonly phase: "submitting" })
  | (ExerciseFields & { readonly phase: "thinking" })
  | { readonly cause: FailureCause; readonly message: string; readonly phase: "error"; readonly retry: Retry }
  | { readonly phase: "idle" }
  | { readonly phase: "loading" }
  | { readonly phase: "nothing_eligible" };

export type ReportedOutcome = "got_it" | "missed_it";

type Retry =
  | {
      readonly attempt: number;
      readonly exercise: LessonExercise;
      readonly kind: "clips" | "submit";
      readonly missed: boolean;
      readonly welshPlayback: WelshPlayback;
    }
  | { readonly kind: "next" };

/** The woman's Welsh at a standard pace, the man's slowly, or hers and then his. */
export type WelshPlayback = "both" | "slow" | "standard";

/** The phases the position in a track can put the lesson in, in the order a track plays them. */
export type PositionPhase = Extract<
  LessonState["phase"],
  | "awaiting_outcome"
  | "between_welsh"
  | "playing_english"
  | "playing_welsh_slow"
  | "playing_welsh_standard"
  | "submitting"
  | "thinking"
>;

/** Where each phase starts in a track, in seconds. The last one, ``submitting``, starts where the tail does. */
export type Timeline = readonly TimelineEntry[];

type TimelineEntry = { readonly phase: PositionPhase; readonly startsAt: number };
