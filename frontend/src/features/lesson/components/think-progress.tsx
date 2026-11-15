import Box from "@mui/material/Box";

import type { LessonState } from "../types";

import { isExerciseState } from "../stores/lesson-reducer";
import { thinkSeconds } from "../utils/think-time";
import { ThinkProgressFill } from "./think-progress-fill";

/** Shows how long is left to say the Welsh. It is empty at every other time. */
type ThinkProgressProps = { readonly multiplier: number; readonly state: LessonState };

export function ThinkProgress({ multiplier, state }: ThinkProgressProps) {
  if (!isExerciseState(state)) {
    return null;
  }

  return (
    <Box aria-hidden sx={{ bgcolor: "action.hover", borderRadius: 1, height: 16, overflow: "hidden" }}>
      {state.phase === "thinking" ? (
        <ThinkProgressFill paused={state.paused} seconds={thinkSeconds(state.exercise.welsh, multiplier)} />
      ) : null}
    </Box>
  );
}
