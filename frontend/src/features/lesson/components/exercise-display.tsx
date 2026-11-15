import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";

import { TEST_IDS } from "@/config/test-ids";

import type { LessonState } from "../types";

import { NOTHING_ELIGIBLE_MESSAGE } from "../constants";
import { isExerciseState } from "../stores/lesson-reducer";

const LINE_HEIGHT = "1.6em";

/** The text takes a fixed space, one line each, so the buttons below it never move. */
type ExerciseDisplayProps = { readonly state: LessonState };

export function ExerciseDisplay({ state }: ExerciseDisplayProps) {
  const exercise = isExerciseState(state) ? state : null;

  return (
    <>
      <Stack spacing={3}>
        <Typography component="p" data-testid={TEST_IDS.english} noWrap sx={{ height: LINE_HEIGHT }} variant="h5">
          {exercise?.exercise.english}
        </Typography>
        <Typography component="p" data-testid={TEST_IDS.welsh} noWrap sx={{ height: LINE_HEIGHT }} variant="h5">
          {exercise?.revealed === true ? exercise.exercise.welsh : null}
        </Typography>
      </Stack>
      {state.phase === "nothing_eligible" ? <Typography>{NOTHING_ELIGIBLE_MESSAGE}</Typography> : null}
      {state.phase === "error" ? (
        <Typography color="error" role="alert">
          {state.message}
        </Typography>
      ) : null}
    </>
  );
}
