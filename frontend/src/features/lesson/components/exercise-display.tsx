import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";

import type { LessonState } from "../types";

import { isExerciseState } from "../stores/lesson-reducer";

const LINE_HEIGHT = "1.6em";

/** The text takes a fixed space, one line each, so the buttons below it never move. */
export function ExerciseDisplay({ state }: { readonly state: LessonState }) {
  const exercise = isExerciseState(state) ? state : null;

  return (
    <>
      <Stack spacing={3}>
        <Typography noWrap sx={{ height: LINE_HEIGHT }} variant="h5">
          {exercise?.exercise.english}
        </Typography>
        <Typography noWrap sx={{ height: LINE_HEIGHT }} variant="h5">
          {exercise?.revealed === true ? exercise.exercise.welsh : null}
        </Typography>
      </Stack>
      {state.phase === "nothing_eligible" ? <Typography>{state.reason}</Typography> : null}
      {state.phase === "error" ? <Typography color="error">{state.message}</Typography> : null}
    </>
  );
}
