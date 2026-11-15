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
  audio: { english: "/e", welsh: "/w", welsh_slow: "/s" },
  english: "I can go",
  selectionId: "selection-1",
  welsh: "Galla i fynd",
};

const READY = { english: "ready", welsh: "ready", welsh_slow: "ready" } as const;

function exerciseState(phase: ExerciseState["phase"], overrides: Partial<ExerciseState> = {}): ExerciseState {
  return {
    attempt: 0,
    clips: READY,
    exercise: EXERCISE,
    missed: false,
    paused: false,
    phase,
    replayCount: 0,
    revealed: false,
    slowWelshEnabled: true,
    ...(phase === "waiting_for_clip" ? { track: "welsh" } : {}),
    ...overrides,
  } as ExerciseState;
}

function run(state: LessonState, ...events: readonly LessonEvent[]): LessonState {
  return events.reduce(lessonReducer, state);
}

describe("the happy path", () => {
  it("plays English, thinks, plays both Welsh clips, waits for the outcome and submits", () => {
    const phases: string[] = [];
    let state: LessonState = INITIAL_LESSON_STATE;
    const events: readonly LessonEvent[] = [
      { type: "start" },
      { exercise: EXERCISE, slowWelshEnabled: true, type: "next_loaded" },
      { track: "welsh", type: "clip_ready" },
      { track: "welsh_slow", type: "clip_ready" },
      { track: "english", type: "clip_ready" },
      { type: "clip_ended" },
      { type: "think_elapsed" },
      { type: "clip_ended" },
      { type: "gap_elapsed" },
      { type: "clip_ended" },
      { type: "window_elapsed" },
      { type: "submitted" },
    ];

    for (const event of events) {
      state = lessonReducer(state, event);
      phases.push(state.phase);
    }

    expect(phases).toEqual([
      "loading",
      "preparing",
      "preparing",
      "preparing",
      "playing_english",
      "thinking",
      "playing_welsh",
      "between_welsh",
      "playing_welsh_slow",
      "awaiting_outcome",
      "submitting",
      "loading",
    ]);
  });

  it("waits in preparing until the English is ready", () => {
    const state = run(
      INITIAL_LESSON_STATE,
      { type: "start" },
      { exercise: EXERCISE, slowWelshEnabled: true, type: "next_loaded" },
      { track: "welsh", type: "clip_ready" },
    );

    expect(state.phase).toBe("preparing");
  });

  it("starts the next exercise unmarked", () => {
    const state = run(
      exerciseState("submitting", { missed: true }),
      { type: "submitted" },
      { exercise: EXERCISE, slowWelshEnabled: true, type: "next_loaded" },
    );

    expect(state).toMatchObject({ missed: false, phase: "preparing", revealed: false });
  });
});

describe("a clip that is not ready when it is needed", () => {
  it("waits for the Welsh when think time ends first, then plays it", () => {
    const loading = exerciseState("thinking", { clips: { ...READY, welsh: "loading" } });

    const waiting = lessonReducer(loading, { type: "think_elapsed" });

    expect(waiting).toMatchObject({ phase: "waiting_for_clip", track: "welsh" });
    expect(lessonReducer(waiting, { track: "welsh", type: "clip_ready" }).phase).toBe("playing_welsh");
  });

  it("does not play a clip that arrives while paused until resumed", () => {
    const waiting = exerciseState("waiting_for_clip", {
      clips: { ...READY, welsh: "loading" },
      paused: true,
      track: "welsh",
    });

    const arrived = lessonReducer(waiting, { track: "welsh", type: "clip_ready" });

    expect(arrived.phase).toBe("waiting_for_clip");
    expect(lessonReducer(arrived, { type: "toggle_pause" }).phase).toBe("playing_welsh");
  });

  it("stops with an error when the clip needed failed to load", () => {
    const waiting = exerciseState("waiting_for_clip", {
      clips: { ...READY, welsh: "loading" },
      track: "welsh",
    });

    expect(lessonReducer(waiting, { cause: "other", track: "welsh", type: "clip_failed" })).toMatchObject({
      phase: "error",
      retry: { kind: "clips" },
    });
  });

  it("stops at once when the English fails, but notes a Welsh failure until it is needed", () => {
    const preparing = exerciseState("preparing", {
      clips: { english: "loading", welsh: "loading", welsh_slow: "loading" },
    });

    expect(lessonReducer(preparing, { cause: "other", track: "english", type: "clip_failed" }).phase).toBe("error");

    const noted = lessonReducer(preparing, { cause: "other", track: "welsh", type: "clip_failed" });

    expect(noted.phase).toBe("preparing");
    expect(
      lessonReducer({ ...exerciseState("thinking"), clips: { ...READY, welsh: "failed" } }, { type: "think_elapsed" })
        .phase,
    ).toBe("error");
    expect(noted).toMatchObject({ clips: { welsh: "failed" } });
  });

  it("retries the clips with a new attempt, keeping the missed mark", () => {
    const failed = lessonReducer(exerciseState("preparing", { missed: true }), {
      cause: "other",
      track: "english",
      type: "clip_failed",
    });

    expect(lessonReducer(failed, { type: "retry" })).toMatchObject({ attempt: 1, missed: true, phase: "preparing" });
  });
});

describe("pausing", () => {
  it.each([
    "playing_english",
    "thinking",
    "playing_welsh",
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
    expect(isPausable(state)).toBe(false);
  });

  it("ignores clip ends and timers while paused", () => {
    for (const [phase, event] of [
      ["playing_english", "clip_ended"],
      ["thinking", "think_elapsed"],
      ["between_welsh", "gap_elapsed"],
      ["awaiting_outcome", "window_elapsed"],
    ] as const) {
      const paused = exerciseState(phase, { paused: true });

      expect(lessonReducer(paused, { type: event })).toBe(paused);
    }
  });
});

describe("marking missed", () => {
  it.each(["playing_welsh", "between_welsh", "playing_welsh_slow", "awaiting_outcome"] as const)(
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

  it("is accepted between the two Welsh clips but not before the first", () => {
    expect(canMarkMissed(exerciseState("waiting_for_clip", { track: "welsh_slow" }))).toBe(true);
    expect(canMarkMissed(exerciseState("waiting_for_clip", { track: "welsh" }))).toBe(false);
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

  it("counts a replay of the English too, so it starts again", () => {
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

describe("the gap between the Welsh clips", () => {
  it("shows the Welsh text and plays the slow Welsh when the gap ends", () => {
    const gap = lessonReducer(exerciseState("playing_welsh"), { type: "clip_ended" });

    expect(gap).toMatchObject({ phase: "between_welsh", revealed: false });
    expect(lessonReducer(gap, { type: "gap_elapsed" })).toMatchObject({ phase: "playing_welsh_slow", revealed: true });
  });

  it("shows the text even when it has to wait for the slow Welsh", () => {
    const gap = exerciseState("between_welsh", { clips: { ...READY, welsh_slow: "loading" } });

    expect(lessonReducer(gap, { type: "gap_elapsed" })).toMatchObject({
      phase: "waiting_for_clip",
      revealed: true,
      track: "welsh_slow",
    });
  });

  it("keeps the Welsh showing on a replay, and hides it for the next exercise", () => {
    const replayed = lessonReducer(exerciseState("awaiting_outcome", { revealed: true }), { type: "replay" });

    expect(replayed).toMatchObject({ phase: "playing_english", revealed: true });
    expect(
      run(
        exerciseState("submitting", { revealed: true }),
        { type: "submitted" },
        { exercise: EXERCISE, slowWelshEnabled: true, type: "next_loaded" },
      ),
    ).toMatchObject({ revealed: false });
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

  it("fails when playback is refused during a clip", () => {
    expect(lessonReducer(exerciseState("playing_welsh"), { type: "playback_failed" })).toMatchObject({
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
    const speech = lessonReducer(exerciseState("preparing"), {
      cause: "speech_unavailable",
      track: "english",
      type: "clip_failed",
    });

    expect(missing).toMatchObject({ cause: "learner_missing", phase: "error" });
    expect(speech).toMatchObject({
      cause: "speech_unavailable",
      message: expect.stringContaining("speech service") as string,
    });
  });

  it("resets to idle from anywhere", () => {
    expect(lessonReducer(exerciseState("thinking"), { type: "reset" })).toEqual(INITIAL_LESSON_STATE);
  });

  it("ignores events that do not apply, returning the same state", () => {
    expect(lessonReducer(INITIAL_LESSON_STATE, { type: "clip_ended" })).toBe(INITIAL_LESSON_STATE);
    expect(lessonReducer(INITIAL_LESSON_STATE, { type: "submitted" })).toBe(INITIAL_LESSON_STATE);
    expect(isExerciseState(INITIAL_LESSON_STATE)).toBe(false);
  });
});

describe("with the slow Welsh turned off", () => {
  it("goes from the Welsh straight to the outcome window and shows the text", () => {
    const playing = exerciseState("playing_welsh", { slowWelshEnabled: false });

    expect(lessonReducer(playing, { type: "clip_ended" })).toMatchObject({
      phase: "awaiting_outcome",
      revealed: true,
    });
  });

  it("still goes through the pause and the slow Welsh when it is on", () => {
    const playing = exerciseState("playing_welsh");

    expect(lessonReducer(playing, { type: "clip_ended" })).toMatchObject({ phase: "between_welsh", revealed: false });
  });

  it("keeps the setting the exercise was loaded with, through a retry", () => {
    const failed = run(
      exerciseState("preparing", { slowWelshEnabled: false }),
      { cause: "other", track: "english", type: "clip_failed" },
      { type: "retry" },
    );

    expect(failed).toMatchObject({ phase: "preparing", slowWelshEnabled: false });
  });

  it("takes the setting from the event that loads the exercise", () => {
    const state = run(
      INITIAL_LESSON_STATE,
      { type: "start" },
      { exercise: EXERCISE, slowWelshEnabled: false, type: "next_loaded" },
    );

    expect(state).toMatchObject({ phase: "preparing", slowWelshEnabled: false });
  });

  it("lets the learner mark it missed during the Welsh and the outcome window", () => {
    expect(canMarkMissed(exerciseState("awaiting_outcome", { slowWelshEnabled: false }))).toBe(true);
  });
});
