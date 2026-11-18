import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";

import { TEST_IDS } from "@/config/test-ids";

import type { LessonActions } from "../hooks/use-lesson-player";
import type { LessonState } from "../types";

import { isExerciseState } from "../stores/lesson-reducer";

type LessonControlsProps = {
  readonly actions: LessonActions;
  readonly canMiss: boolean;
  readonly canPause: boolean;
  readonly state: LessonState;
};

export function LessonControls({ actions, canMiss, canPause, state }: LessonControlsProps) {
  if (state.phase === "error") {
    return state.cause === "learner_missing" ? null : (
      <Button onClick={actions.retry} size="large" variant="contained">
        Retry
      </Button>
    );
  }

  if (!isExerciseState(state)) {
    return null;
  }

  return (
    <Stack spacing={2}>
      <Button
        color={state.missed ? "error" : "warning"}
        data-testid={TEST_IDS.missedIt}
        disabled={!canMiss && !state.missed}
        onClick={actions.missed}
        size="large"
        sx={{ minHeight: 72 }}
        variant="contained"
      >
        {state.missed ? "Marked as missed" : "Missed it (M)"}
      </Button>
      <Stack direction="row" spacing={2}>
        <Button disabled={!canPause} onClick={actions.togglePause} variant="outlined">
          {state.paused ? "Resume" : "Pause"} (Space)
        </Button>
        <Button disabled={!canPause} onClick={actions.replay} variant="outlined">
          Replay (R)
        </Button>
      </Stack>
    </Stack>
  );
}
