import { describe, expect, it } from "vitest";

import type { ExerciseState, LessonEvent, LessonExercise, LessonState } from "@/features/lesson/types";

import {
  canMarkMissed,
  INITIAL_LESSON_STATE,
  isExerciseState,
  isPausable,
  lessonReducer,
} from "@/features/lesson/stores/lesson-reducer";

const EXERCISE: LessonExercise = {
  audio: { english: "/e", welsh_slow: "/s", welsh_standard: "/w" },
  english: "I can go",
  exerciseId: "galla-fynd",
  selectionId: "selection-1",
  welsh: "Galla i fynd",
};

function exerciseState(phase: ExerciseState["phase"], overrides: Partial<ExerciseState> = {}): ExerciseState {
  return {
    attempt: 0,
    exercise: EXERCISE,
    missed: false,
    paused: false,
    phase,
    replayCount: 0,
    revealed: false,
    welshPlayback: "both",
    ...overrides,
  };
}

function run(state: LessonState, ...events: readonly LessonEvent[]): LessonState {
  return events.reduce(lessonReducer, state);
}

describe("the happy path", () => {
  it("plays the English, thinks, plays both Welsh clips, waits for the outcome and submits", () => {
    const phases: string[] = [];
    let state: LessonState = INITIAL_LESSON_STATE;
    const events: readonly LessonEvent[] = [
      { type: "start" },
      { exercise: EXERCISE, type: "next_loaded", welshPlayback: "both" },
      { type: "track_ready" },
      { phase: "thinking", type: "position_reached" },
      { phase: "playing_welsh_standard", type: "position_reached" },
      { phase: "between_welsh", type: "position_reached" },
      { phase: "playing_welsh_slow", type: "position_reached" },
      { phase: "awaiting_outcome", type: "position_reached" },
      { phase: "submitting", type: "position_reached" },
      { type: "submitted" },
    ];

    for (const event of events) {
      state = lessonReducer(state, event);
      phases.push(state.phase);
    }

    expect(phases).toEqual([
      "loading",
      "preparing",
      "playing_english",
      "thinking",
      "playing_welsh_standard",
      "between_welsh",
      "playing_welsh_slow",
      "awaiting_outcome",
      "submitting",
      "loading",
    ]);
  });

  it("waits in preparing until the track is ready", () => {
    const state = run(
      INITIAL_LESSON_STATE,
      { type: "start" },
      { exercise: EXERCISE, type: "next_loaded", welshPlayback: "both" },
    );

    expect(state.phase).toBe("preparing");
  });

  it("starts the next exercise unmarked", () => {
    const state = run(
      exerciseState("submitting", { missed: true }),
      { type: "submitted" },
      { exercise: EXERCISE, type: "next_loaded", welshPlayback: "both" },
    );

    expect(state).toMatchObject({ missed: false, phase: "preparing", revealed: false });
  });
});

describe("the position in the track", () => {
  it("jumps ahead over the phases the page was not running for", () => {
    const state = lessonReducer(exerciseState("thinking"), { phase: "awaiting_outcome", type: "position_reached" });

    expect(state.phase).toBe("awaiting_outcome");
  });

  it("never moves back, or restarts the phase it is in", () => {
    const state = exerciseState("playing_welsh_slow");

    expect(lessonReducer(state, { phase: "thinking", type: "position_reached" })).toBe(state);
    expect(lessonReducer(state, { phase: "playing_welsh_slow", type: "position_reached" })).toBe(state);
  });

  it("is ignored while paused, and while no track plays", () => {
    const paused = exerciseState("thinking", { paused: true });
    const preparing = exerciseState("preparing");

    expect(lessonReducer(paused, { phase: "playing_welsh_standard", type: "position_reached" })).toBe(paused);
    expect(lessonReducer(preparing, { phase: "submitting", type: "position_reached" })).toBe(preparing);
    expect(lessonReducer(INITIAL_LESSON_STATE, { phase: "thinking", type: "position_reached" })).toBe(
      INITIAL_LESSON_STATE,
    );
  });

  it("is ignored once the outcome is being sent", () => {
    const state = exerciseState("submitting");

    expect(lessonReducer(state, { phase: "awaiting_outcome", type: "position_reached" })).toBe(state);
  });
});

describe("which Welsh shows, and when", () => {
  it("shows the text only for the man's recording when both play", () => {
    const woman = lessonReducer(exerciseState("thinking"), {
      phase: "playing_welsh_standard",
      type: "position_reached",
    });
    const gap = lessonReducer(woman, { phase: "between_welsh", type: "position_reached" });
    const man = lessonReducer(gap, { phase: "playing_welsh_slow", type: "position_reached" });

    expect([woman, gap, man].map((state) => isExerciseState(state) && state.revealed)).toEqual([false, false, true]);
  });

  it("shows the text as the woman starts with standard only", () => {
    const woman = lessonReducer(exerciseState("thinking", { welshPlayback: "standard" }), {
      phase: "playing_welsh_standard",
      type: "position_reached",
    });

    expect(woman).toMatchObject({ phase: "playing_welsh_standard", revealed: true });
  });

  it("shows the text as the man starts with slow only", () => {
    const man = lessonReducer(exerciseState("thinking", { welshPlayback: "slow" }), {
      phase: "playing_welsh_slow",
      type: "position_reached",
    });

    expect(man).toMatchObject({ phase: "playing_welsh_slow", revealed: true });
  });

  it("shows the text when the position skipped past the Welsh", () => {
    const state = lessonReducer(exerciseState("thinking", { welshPlayback: "standard" }), {
      phase: "awaiting_outcome",
      type: "position_reached",
    });

    expect(state).toMatchObject({ revealed: true });
  });

  it("keeps the Welsh showing on a replay, and hides it for the next exercise", () => {
    const replayed = lessonReducer(exerciseState("awaiting_outcome", { revealed: true }), { type: "replay" });

    expect(replayed).toMatchObject({ phase: "playing_english", revealed: true });
    expect(
      run(
        exerciseState("submitting", { revealed: true }),
        { type: "submitted" },
        { exercise: EXERCISE, type: "next_loaded", welshPlayback: "both" },
      ),
    ).toMatchObject({ revealed: false });
  });

  it("takes the setting from the event that loads the exercise", () => {
    const state = run(
      INITIAL_LESSON_STATE,
      { type: "start" },
      { exercise: EXERCISE, type: "next_loaded", welshPlayback: "standard" },
    );

    expect(state).toMatchObject({ phase: "preparing", welshPlayback: "standard" });
  });
});

describe("a track that cannot be made", () => {
  it("stops with an error that says the audio could not be loaded", () => {
    expect(lessonReducer(exerciseState("preparing"), { cause: "other", type: "track_failed" })).toMatchObject({
      message: "The audio could not be loaded",
      phase: "error",
      retry: { kind: "clips" },
    });
  });

  it("retries with a new attempt, keeping the missed mark and the setting", () => {
    const failed = lessonReducer(exerciseState("preparing", { missed: true, welshPlayback: "slow" }), {
      cause: "other",
      type: "track_failed",
    });

    expect(lessonReducer(failed, { type: "retry" })).toMatchObject({
      attempt: 1,
      missed: true,
      phase: "preparing",
      welshPlayback: "slow",
    });
  });

  it("ignores a track that arrives when none is wanted", () => {
    const state = exerciseState("thinking");

    expect(lessonReducer(state, { type: "track_ready" })).toBe(state);
    expect(lessonReducer(state, { cause: "other", type: "track_failed" })).toBe(state);
  });

  it("says why when the speech service is down", () => {
    expect(
      lessonReducer(exerciseState("preparing"), { cause: "speech_unavailable", type: "track_failed" }),
    ).toMatchObject({ cause: "speech_unavailable", message: expect.stringContaining("speech service") as string });
  });
});

describe("pausing", () => {
  it.each([
    "playing_english",
    "thinking",
    "playing_welsh_standard",
    "between_welsh",
    "playing_welsh_slow",
    "awaiting_outcome",
  ] as const)("pauses and resumes in %s", (phase) => {
    const paused = lessonReducer(exerciseState(phase), { type: "toggle_pause" });

    expect(paused).toMatchObject({ paused: true, phase });
    expect(lessonReducer(paused, { type: "toggle_pause" })).toMatchObject({ paused: false, phase });
  });

  it.each(["preparing", "submitting"] as const)("cannot pause in %s", (phase) => {
    const state = exerciseState(phase);

    expect(lessonReducer(state, { type: "toggle_pause" })).toBe(state);
    expect(lessonReducer(state, { type: "pause" })).toBe(state);
    expect(isPausable(state)).toBe(false);
  });

  it("pauses and resumes by event, as when the lock screen does it, without undoing itself", () => {
    const paused = lessonReducer(exerciseState("thinking"), { type: "pause" });

    expect(lessonReducer(paused, { type: "pause" })).toBe(paused);
    expect(paused).toMatchObject({ paused: true });
    expect(lessonReducer(paused, { type: "resume" })).toMatchObject({ paused: false });
    expect(lessonReducer(exerciseState("thinking"), { type: "resume" })).toMatchObject({ paused: false });
  });
});

describe("marking missed", () => {
  it.each(["playing_welsh_standard", "between_welsh", "playing_welsh_slow", "awaiting_outcome"] as const)(
    "is accepted in %s and kept to the end",
    (phase) => {
      const marked = lessonReducer(exerciseState(phase), { type: "missed" });

      expect(marked).toMatchObject({ missed: true, phase });
    },
  );

  it.each(["playing_english", "thinking", "preparing", "submitting"] as const)("is ignored in %s", (phase) => {
    const state = exerciseState(phase);

    expect(canMarkMissed(state)).toBe(false);
    expect(lessonReducer(state, { type: "missed" })).toBe(state);
  });

  it("survives a replay", () => {
    const state = run(exerciseState("awaiting_outcome", { missed: true }), { type: "replay" });

    expect(state).toMatchObject({ missed: true, phase: "playing_english" });
  });
});

describe("replay", () => {
  it("restarts from the English, unpaused, and counts the replay", () => {
    const state = lessonReducer(exerciseState("thinking", { paused: true }), { type: "replay" });

    expect(state).toMatchObject({ paused: false, phase: "playing_english", replayCount: 1 });
  });

  it("counts a replay of the English too", () => {
    const state = run(exerciseState("playing_english"), { type: "replay" }, { type: "replay" });

    expect(state).toMatchObject({ replayCount: 2 });
  });

  it("is ignored while submitting", () => {
    const state = exerciseState("submitting");

    expect(lessonReducer(state, { type: "replay" })).toBe(state);
  });
});

describe("the outcome window", () => {
  it("can be skipped", () => {
    expect(lessonReducer(exerciseState("awaiting_outcome"), { type: "skip_window" }).phase).toBe("submitting");
  });

  it("cannot be skipped while paused", () => {
    const state = exerciseState("awaiting_outcome", { paused: true });

    expect(lessonReducer(state, { type: "skip_window" })).toBe(state);
  });
});

describe("errors", () => {
  it("shows an error and retries the request when the next exercise fails", () => {
    const failed = run(INITIAL_LESSON_STATE, { type: "start" }, { cause: "other", type: "next_failed" });

    expect(failed).toMatchObject({ phase: "error", retry: { kind: "next" } });
    expect(lessonReducer(failed, { type: "retry" })).toEqual({ phase: "loading" });
  });

  it("keeps the exercise and the missed mark when submitting fails, and resubmits on retry", () => {
    const failed = lessonReducer(exerciseState("submitting", { missed: true }), {
      cause: "other",
      type: "submit_failed",
    });

    expect(failed).toMatchObject({ phase: "error", retry: { kind: "submit", missed: true } });
    expect(lessonReducer(failed, { type: "retry" })).toMatchObject({ missed: true, phase: "submitting" });
  });

  it("fails when playback is refused during a track", () => {
    expect(lessonReducer(exerciseState("playing_welsh_standard"), { type: "playback_failed" })).toMatchObject({
      message: "The audio could not be played",
      phase: "error",
    });
  });
});

describe("other states", () => {
  it("reports nothing eligible, and stays there", () => {
    const state = run(INITIAL_LESSON_STATE, { type: "start" }, { type: "nothing_eligible" });

    expect(state).toEqual({ phase: "nothing_eligible" });
    expect(lessonReducer(state, { type: "start" })).toBe(state);
  });

  it("says why a failure happened, when it is known", () => {
    const missing = run(INITIAL_LESSON_STATE, { type: "start" }, { cause: "learner_missing", type: "next_failed" });

    expect(missing).toMatchObject({ cause: "learner_missing", phase: "error" });
  });

  it("resets to idle from anywhere", () => {
    expect(lessonReducer(exerciseState("thinking"), { type: "reset" })).toEqual(INITIAL_LESSON_STATE);
  });

  it("ignores events that do not apply, returning the same state", () => {
    expect(lessonReducer(INITIAL_LESSON_STATE, { type: "track_ready" })).toBe(INITIAL_LESSON_STATE);
    expect(lessonReducer(INITIAL_LESSON_STATE, { type: "submitted" })).toBe(INITIAL_LESSON_STATE);
    expect(isExerciseState(INITIAL_LESSON_STATE)).toBe(false);
  });
});
