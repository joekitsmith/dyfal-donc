import { describe, expect, it } from "vitest";

import { actionForKey } from "@/features/lesson/utils/key-map";

describe("actionForKey", () => {
  it.each([
    [" ", "toggle_pause"],
    ["m", "missed"],
    ["M", "missed"],
    ["r", "replay"],
    ["t", "toggle_reveal"],
    ["n", "skip_window"],
  ])("maps %j to %s", (key, action) => {
    expect(actionForKey(key)).toBe(action);
  });

  it("ignores other keys", () => {
    expect(actionForKey("x")).toBeUndefined();
  });
});
