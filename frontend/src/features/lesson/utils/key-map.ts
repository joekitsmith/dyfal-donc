import type { LessonEvent } from "../types";

export type KeyAction = Extract<LessonEvent["type"], "missed" | "replay" | "skip_window" | "toggle_pause">;

const ACTION_FOR_KEY: Readonly<Record<string, KeyAction>> = {
  " ": "toggle_pause",
  m: "missed",
  n: "skip_window",
  r: "replay",
};

export function actionForKey(key: string): KeyAction | undefined {
  return ACTION_FOR_KEY[key.toLowerCase()];
}
