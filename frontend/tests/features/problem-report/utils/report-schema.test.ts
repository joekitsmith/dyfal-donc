import { describe, expect, it } from "vitest";

import { ApiError } from "@/api/api-error";
import { DESCRIPTION_MAXIMUM_LENGTH } from "@/features/problem-report/constants";
import { reportSchema } from "@/features/problem-report/utils/report-schema";
import { sendFailureMessage } from "@/features/problem-report/utils/send-failure-message";
import { toRequestBody } from "@/features/problem-report/utils/to-request-body";

const FORM = { category: "grammar", description: "The verb is wrong", subjectId: "" };
const VALID = reportSchema.parse(FORM);

describe("reportSchema", () => {
  it("accepts a category and a description", () => {
    expect(reportSchema.safeParse(FORM).success).toBe(true);
  });

  it.each([
    ["no category", { category: "" }],
    ["an empty description", { description: "" }],
    ["a blank description", { description: "   " }],
    ["a description that is too long", { description: "x".repeat(DESCRIPTION_MAXIMUM_LENGTH + 1) }],
  ])("rejects %s", (_name, changes) => {
    expect(reportSchema.safeParse({ ...FORM, ...changes }).success).toBe(false);
  });
});

describe("reportSchema messages", () => {
  function messageFor(changes: object): string | undefined {
    const result = reportSchema.safeParse({ ...FORM, ...changes });

    return result.success ? undefined : result.error.issues[0]?.message;
  }

  it("asks for a kind of problem", () => {
    expect(messageFor({ category: "" })).toBe("Choose a kind of problem.");
  });

  it("asks what is wrong", () => {
    expect(messageFor({ description: "  " })).toBe("Say what is wrong.");
  });

  it("says when it is too long", () => {
    expect(messageFor({ description: "x".repeat(DESCRIPTION_MAXIMUM_LENGTH + 1) })).toBe(
      "That's too long. Keep it under 1,000 characters.",
    );
  });
});

describe("toRequestBody", () => {
  const sentence = { audio: null, english: "E", id: "ex-1", kind: "sentence", welsh: "W" } as const;
  const item = { ...sentence, id: "lex:siarad", kind: "item" } as const;

  it("names the exercise for a sentence", () => {
    expect(toRequestBody("lesson", sentence, reportSchema.parse({ ...FORM, description: " Odd " }))).toEqual({
      category: "grammar",
      description: "Odd",
      exercise_id: "ex-1",
      item_id: null,
      source: "lesson",
    });
  });

  it("names the item for a word", () => {
    expect(toRequestBody("item", item, VALID)).toMatchObject({ exercise_id: null, item_id: "lex:siarad" });
  });

  it("names neither when the report is not about one thing", () => {
    expect(toRequestBody("general", undefined, VALID)).toMatchObject({ exercise_id: null, item_id: null });
  });
});

describe("sendFailureMessage", () => {
  it("says when there have been too many reports", () => {
    expect(sendFailureMessage(new ApiError(429))).toBe("Too many reports. Try again in a minute.");
  });

  it("is plain about any other failure", () => {
    expect(sendFailureMessage(new ApiError(500))).toBe("The report couldn't be sent.");
  });
});
