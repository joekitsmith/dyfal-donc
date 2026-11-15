import { useEffect } from "react";

import { actionForKey, type KeyAction } from "../utils/key-map";

const EDITABLE_SELECTOR = "input, textarea, select, [role='slider'], [contenteditable='true']";

/** Reports the lesson's shortcuts. Combinations with Ctrl, Cmd or Alt are left to the browser. */
export function useLessonKeyboard(onAction: (action: KeyAction) => void) {
  useEffect(() => {
    function handle(event: KeyboardEvent) {
      const action = actionForKey(event.key);
      const target = event.target instanceof Element ? event.target : null;

      if (
        action === undefined ||
        event.ctrlKey ||
        event.metaKey ||
        event.altKey ||
        target?.matches(EDITABLE_SELECTOR)
      ) {
        return;
      }

      // Space would also press a focused button, on key up
      if (event.key === " ") {
        event.preventDefault();
      }

      if (event.type === "keydown" && !event.repeat) {
        onAction(action);
      }
    }

    window.addEventListener("keydown", handle);
    window.addEventListener("keyup", handle);

    return () => {
      window.removeEventListener("keydown", handle);
      window.removeEventListener("keyup", handle);
    };
  }, [onAction]);
}
