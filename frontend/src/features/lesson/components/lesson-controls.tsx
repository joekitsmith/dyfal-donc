import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";

import type { LessonActions } from "../hooks/use-lesson-player";
import type { LessonState } from "../types";

import { isExerciseState } from "../stores/lesson-reducer";

export function LessonControls({
  actions,
  canMiss,
  canPause,
  state,
}: {
  readonly actions: LessonActions;
  readonly canMiss: boolean;
  readonly canPause: boolean;
  readonly state: LessonState;
}) {
  if (state.phase === "idle" || state.phase === "nothing_eligible") {
    return (
      <Button onClick={actions.start} size="large" variant="contained">
        {state.phase === "idle" ? "Start" : "Check again"}
      </Button>
    );
  }

  if (state.phase === "error") {
    return (
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
        color="warning"
        disabled={!canMiss}
        onClick={actions.missed}
        size="large"
        sx={{ minHeight: 72 }}
        variant="contained"
      >
        Missed it (M)
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
