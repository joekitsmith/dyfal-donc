import type { CLIP_TRACKS } from "./constants";

type ClipLinks = Readonly<Record<ClipTrack, string>>;

type ClipStatus = "failed" | "loading" | "ready";

export type ClipTrack = (typeof CLIP_TRACKS)[number];

export type ExerciseFields = {
  /** Counts retries of the clips, so a retry fetches them again. */
  readonly attempt: number;
  readonly clips: Readonly<Record<ClipTrack, ClipStatus>>;
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
  | { readonly cause: FailureCause; readonly track: ClipTrack; readonly type: "clip_failed" }
  | { readonly cause: FailureCause; readonly type: "next_failed" | "submit_failed" }
  | { readonly exercise: LessonExercise; readonly type: "next_loaded"; readonly welshPlayback: WelshPlayback }
  | { readonly track: ClipTrack; readonly type: "clip_ready" }
  | {
      readonly type:
        | "clip_ended"
        | "gap_elapsed"
        | "missed"
        | "nothing_eligible"
        | "playback_failed"
        | "replay"
        | "reset"
        | "retry"
        | "skip_window"
        | "start"
        | "submitted"
        | "think_elapsed"
        | "toggle_pause"
        | "window_elapsed";
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
  | (ExerciseFields & { readonly phase: "waiting_for_clip"; readonly track: WaitingTrack })
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

export type WaitingTrack = "welsh_slow" | "welsh_standard";
