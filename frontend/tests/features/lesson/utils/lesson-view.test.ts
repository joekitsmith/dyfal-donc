import { describe, expect, it } from "vitest";

import type { ExerciseState, LessonExercise, LessonState, WelshPlayback } from "@/features/lesson/types";

import { beatRowProps, lessonView } from "@/features/lesson/utils/lesson-view";

const EXERCISE: LessonExercise = {
  audio: { english: "/e", welsh_slow: "/s", welsh_standard: "/w" },
  english: "I can go",
  exerciseId: "galla-fynd",
  introducesItem: false,
  selectionId: "selection-1",
  welsh: "Galla i fynd",
};

const NEW_ITEM_EXERCISE: LessonExercise = { ...EXERCISE, introducesItem: true };

function exerciseState(phase: ExerciseState["phase"], overrides: Partial<ExerciseState> = {}): ExerciseState {
  return {
    attempt: 0,
    exercise: EXERCISE,
    isFirst: false,
    missed: false,
    paused: false,
    phase,
    replayCount: 0,
    revealed: false,
    welshPlayback: "both",
    ...overrides,
  };
}

function view(state: LessonState, waitedLong = false) {
  if (state.phase === "idle") {
    throw new Error("The lesson at rest has no view");
  }

  return lessonView(state, waitedLong);
}

describe("before the first exercise", () => {
  it("waits with the first block now while the exercise is fetched", () => {
    expect(view({ phase: "loading" })).toMatchObject({
      beats: { mode: "first-now" },
      caption: "Getting the first one…",
      controls: { look: "unavailable" },
      english: "",
      slab: "waiting",
    });
  });

  it("shows the English as soon as it is known, and keeps waiting for the audio", () => {
    expect(view(exerciseState("preparing", { isFirst: true }))).toMatchObject({
      beats: { count: 6, mode: "first-now" },
      caption: "Getting the first one…",
      controls: { look: "unavailable" },
      english: "I can go",
      slab: "waiting",
      welsh: "",
    });
  });
});

describe("the phases of an exercise with both voices", () => {
  it.each([
    ["playing_english", "all-to-come", "Listen", "waiting"],
    ["thinking", "counting", "Say it in Welsh", "waiting"],
    ["playing_welsh_standard", "all-done", "Now listen", "available"],
    ["between_welsh", "all-done", "Now listen", "available"],
  ] as const)(
    "in %s shows the row %s, the caption %s and the slab %s, without the Welsh",
    (phase, mode, caption, slab) => {
      expect(view(exerciseState(phase))).toMatchObject({
        beats: { mode },
        caption,
        controls: { look: "normal", pause: "pause" },
        english: "I can go",
        next: false,
        slab,
        welsh: "",
      });
    },
  );

  it("opens the row and shows the Welsh when the slow voice starts", () => {
    expect(view(exerciseState("playing_welsh_slow", { revealed: true }))).toMatchObject({
      beats: { mode: "opened" },
      caption: "Once more, slowly",
      slab: "available",
      welsh: "Galla i fynd",
    });
  });

  it("offers Next in the outcome window", () => {
    expect(view(exerciseState("awaiting_outcome", { revealed: true }))).toMatchObject({
      beats: { mode: "opened" },
      caption: "Next one coming up",
      next: true,
      welsh: "Galla i fynd",
    });
  });
});

describe("the Welsh appears when its last recording begins", () => {
  it.each([
    ["standard", "playing_welsh_standard"],
    ["slow", "playing_welsh_slow"],
  ] as const)(
    "with %s only it appears in %s, with the caption Listen and no Now listen step",
    (welshPlayback, phase) => {
      const before = view(exerciseState("thinking", { welshPlayback }));
      const during = view(exerciseState(phase, { revealed: true, welshPlayback }));

      expect(before).toMatchObject({ beats: { mode: "counting" }, welsh: "" });
      expect(during).toMatchObject({
        beats: { mode: "opened" },
        caption: "Listen",
        slab: "available",
        welsh: "Galla i fynd",
      });
    },
  );

  it.each(["standard", "slow", "both"] as const satisfies readonly WelshPlayback[])(
    "never shows it before the recording starts, with %s",
    (welshPlayback) => {
      for (const phase of ["playing_english", "thinking"] as const) {
        expect(view(exerciseState(phase, { welshPlayback })).welsh).toBe("");
      }
    },
  );
});

describe("an exercise that introduces something new", () => {
  it.each(["playing_english", "thinking"] as const)("says so in %s and nowhere else", (phase) => {
    expect(view(exerciseState(phase, { exercise: NEW_ITEM_EXERCISE })).caption).toBe("Something new. Have a guess.");
  });

  it("keeps the usual captions for the Welsh", () => {
    expect(view(exerciseState("playing_welsh_standard", { exercise: NEW_ITEM_EXERCISE })).caption).toBe("Now listen");
  });
});

describe("the exercise after the first, until its audio starts", () => {
  it("has the English phase caption, an empty row, and presses that are ignored rather than shown as unavailable", () => {
    expect(view(exerciseState("preparing"))).toMatchObject({
      beats: { mode: "all-to-come" },
      caption: "Listen",
      controls: { look: "normal" },
      slab: "waiting",
      welsh: "",
    });
  });
});

describe("the slab", () => {
  it("is marked from the press, in every phase, and stays marked through a replay", () => {
    expect(view(exerciseState("playing_welsh_slow", { missed: true, revealed: true })).slab).toBe("marked");
    expect(view(exerciseState("playing_english", { missed: true, revealed: true })).slab).toBe("marked");
  });
});

describe("pausing", () => {
  it("holds everything, says Paused, and offers to resume", () => {
    expect(view(exerciseState("playing_welsh_slow", { paused: true, revealed: true }))).toMatchObject({
      beats: { mode: "opened" },
      caption: "Paused",
      controls: { pause: "resume" },
      next: false,
      paused: true,
      slab: "available",
      welsh: "Galla i fynd",
    });
  });

  it("takes the Next button away while the outcome window is held", () => {
    expect(view(exerciseState("awaiting_outcome", { paused: true, revealed: true })).next).toBe(false);
  });
});

describe("a replay after the Welsh has shown", () => {
  it.each([
    ["playing_english", "Listen"],
    ["thinking", "Say it in Welsh"],
    ["playing_welsh_standard", "Now listen"],
    ["playing_welsh_slow", "Once more, slowly"],
  ] as const)("keeps the row open and the Welsh showing, with the small caption for %s", (phase, caption) => {
    expect(view(exerciseState(phase, { replayCount: 1, revealed: true }))).toMatchObject({
      beats: { mode: "opened" },
      caption,
      welsh: "Galla i fynd",
    });
  });
});

describe("the handover to the next exercise", () => {
  const finished = exerciseState("submitting", { missed: true, revealed: true });

  it("changes nothing while the answer is sent", () => {
    expect(view(finished)).toMatchObject({
      beats: { count: 6, mode: "opened" },
      caption: "Next one coming up",
      controls: { look: "normal" },
      english: "I can go",
      next: false,
      slab: "marked",
      welsh: "Galla i fynd",
    });
  });

  it("changes nothing while the next exercise is fetched, unless it takes long", () => {
    const loading: LessonState = { phase: "loading", previous: finished };

    expect(view(loading)).toEqual(view(finished));
    expect(view(loading, true)).toMatchObject({
      beats: { mode: "first-now" },
      caption: "Getting the next one…",
      controls: { look: "unavailable" },
      english: "",
      slab: "waiting",
      welsh: "",
    });
  });
});

describe("errors", () => {
  const exercise = exerciseState("preparing");

  it.each([
    ["clips", "other", "The audio couldn't be loaded", "retry"],
    ["clips", "speech_unavailable", "The speech service isn't available", "retry"],
    ["submit", "other", "Your answer couldn't be saved", "retry"],
    ["next", "other", "The next sentence couldn't be loaded", "retry"],
    ["clips", "learner_missing", "We couldn't find your progress", "account"],
  ] as const)("for a %s failure with cause %s shows %s with the action %s", (kind, cause, title, action) => {
    const retry =
      kind === "next"
        ? ({ kind } as const)
        : ({ attempt: 0, exercise: EXERCISE, isFirst: false, kind, missed: false, welshPlayback: "both" } as const);
    const result = view({ cause, phase: "error", retry, text: "Text", title });

    expect(result).toMatchObject({
      beats: { mode: "all-to-come" },
      controls: { look: "unavailable" },
      error: { action, title },
      slab: "waiting",
      welsh: "",
    });
  });

  it("keeps the sentence on screen for a failure that does not lose the learner, and empties it for one that does", () => {
    const retry = {
      attempt: 0,
      exercise: EXERCISE,
      isFirst: false,
      kind: "submit",
      missed: false,
      welshPlayback: "both",
    } as const;

    expect(view({ cause: "other", phase: "error", retry, text: "t", title: "T" }).english).toBe("I can go");
    expect(view({ cause: "learner_missing", phase: "error", retry, text: "t", title: "T" }).english).toBe("");
    expect(exercise.phase).toBe("preparing");
  });

  it("says the course is not ready when nothing is eligible, with nothing to press", () => {
    expect(view({ phase: "nothing_eligible" })).toMatchObject({
      english: "",
      error: { action: null, title: "The course isn't ready yet" },
    });
  });
});

describe("beatRowProps", () => {
  it.each([
    ["all-to-come", { count: 6, opened: false, waiting: false }],
    ["counting", { count: 6, nowIndex: 2, opened: false, waiting: false }],
    ["first-now", { count: 6, nowIndex: 0, opened: false, waiting: true }],
    ["all-done", { count: 6, nowIndex: 6, opened: false, waiting: false }],
    ["opened", { count: 6, opened: true, waiting: false }],
  ] as const)("turns the mode %s into the row's settings", (mode, expected) => {
    expect(beatRowProps({ count: 6, mode, run: "" }, 2)).toEqual(expected);
  });
});

describe("the row's run", () => {
  it("is new after a replay, so the row starts again from the first block", () => {
    const first = view(exerciseState("thinking")).beats.run;
    const replayed = view(exerciseState("thinking", { replayCount: 1 })).beats.run;

    expect(replayed).not.toBe(first);
  });
});
