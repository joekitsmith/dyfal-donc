import { renderHook } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { useLessonKeyboard } from "@/features/lesson/hooks/use-lesson-keyboard";

function press(key: string) {
  window.dispatchEvent(new KeyboardEvent("keydown", { key }));
}

describe("useLessonKeyboard", () => {
  afterEach(() => {
    document.body.replaceChildren();
  });

  it("reports a shortcut", () => {
    const onAction = vi.fn();
    renderHook(() => {
      useLessonKeyboard(onAction);
    });

    press("m");

    expect(onAction).toHaveBeenCalledWith("missed");
  });

  it("reports nothing while a dialog is open", () => {
    const dialog = document.createElement("div");
    const onAction = vi.fn();
    dialog.setAttribute("role", "dialog");
    document.body.append(dialog);
    renderHook(() => {
      useLessonKeyboard(onAction);
    });

    press("m");

    expect(onAction).not.toHaveBeenCalled();
  });
});
