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
};

export type ExerciseState = Extract<LessonState, { readonly exercise: LessonExercise }>;

export type LessonEvent =
  | { readonly exercise: LessonExercise; readonly type: "next_loaded" }
  | { readonly reason: string; readonly type: "nothing_eligible" }
  | { readonly track: ClipTrack; readonly type: "clip_failed" }
  | { readonly track: ClipTrack; readonly type: "clip_ready" }
  | {
      readonly type:
        | "clip_ended"
        | "gap_elapsed"
        | "missed"
        | "next_failed"
        | "playback_failed"
        | "replay"
        | "reset"
        | "retry"
        | "skip_window"
        | "start"
        | "submit_failed"
        | "submitted"
        | "think_elapsed"
        | "toggle_pause"
        | "window_elapsed";
    };

export type LessonExercise = {
  readonly audio: ClipLinks;
  readonly english: string;
  readonly selectionId: string;
  readonly welsh: string;
};

export type LessonState =
  | (ExerciseFields & { readonly phase: "awaiting_outcome" })
  | (ExerciseFields & { readonly phase: "between_welsh" })
  | (ExerciseFields & { readonly phase: "playing_english" })
  | (ExerciseFields & { readonly phase: "playing_welsh" })
  | (ExerciseFields & { readonly phase: "playing_welsh_slow" })
  | (ExerciseFields & { readonly phase: "preparing" })
  | (ExerciseFields & { readonly phase: "submitting" })
  | (ExerciseFields & { readonly phase: "thinking" })
  | (ExerciseFields & { readonly phase: "waiting_for_clip"; readonly track: WaitingTrack })
  | { readonly message: string; readonly phase: "error"; readonly retry: Retry }
  | { readonly phase: "idle" }
  | { readonly phase: "loading" }
  | { readonly phase: "nothing_eligible"; readonly reason: string };

export type ReportedOutcome = "got_it" | "missed_it";

type Retry =
  | {
      readonly attempt: number;
      readonly exercise: LessonExercise;
      readonly kind: "clips" | "submit";
      readonly missed: boolean;
    }
  | { readonly kind: "next" };

export type WaitingTrack = "welsh" | "welsh_slow";
