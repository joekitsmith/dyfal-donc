import { describe, expect, it } from "vitest";

import { lessonError } from "@/features/lesson/utils/lesson-error";

describe("lessonError", () => {
  it.each([
    ["clips", "The audio couldn't be loaded"],
    ["next", "The next sentence couldn't be loaded"],
    ["playback", "The audio couldn't be played"],
    ["submit", "Your answer couldn't be saved"],
  ] as const)("says what was being done for %s when the cause is not known", (context, title) => {
    expect(lessonError(context, "other").title).toBe(title);
  });

  it.each(["clips", "next", "playback", "submit"] as const)(
    "puts the cause before what was being done for %s",
    (context) => {
      expect(lessonError(context, "speech_unavailable").title).toBe("The speech service isn't available");
      expect(lessonError(context, "learner_missing").title).toBe("We couldn't find your progress");
    },
  );
});
