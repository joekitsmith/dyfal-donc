import Alert from "@mui/material/Alert";
import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";

import type { MissedExercise } from "../types";

import { useReplayClip } from "../hooks/use-replay-clip";

type MissedExerciseListProps = { readonly exercises: readonly MissedExercise[] };

/** The exercises marked as missed, each with the Welsh to play again. It shows nothing for an empty list. */
export function MissedExerciseList({ exercises }: MissedExerciseListProps) {
  const { failed, play } = useReplayClip();

  if (exercises.length === 0) {
    return null;
  }

  return (
    <Stack aria-label="Missed exercises" component="section" spacing={1}>
      <Typography component="h2" variant="h6">
        Missed exercises
      </Typography>
      {exercises.map((exercise) => (
        <Stack key={exercise.id} spacing={0.5}>
          <Typography>{exercise.english}</Typography>
          <Typography>{exercise.welsh}</Typography>
          <Stack direction="row" spacing={1}>
            <Button
              aria-label={`Play ${exercise.welsh}`}
              onClick={() => {
                play(exercise.audio.welsh.standard);
              }}
              variant="outlined"
            >
              Play
            </Button>
            <Button
              aria-label={`Play ${exercise.welsh} slowly`}
              onClick={() => {
                play(exercise.audio.welsh.slow);
              }}
              variant="outlined"
            >
              Play slowly
            </Button>
          </Stack>
        </Stack>
      ))}
      {failed ? <Alert severity="error">The audio could not be played</Alert> : null}
    </Stack>
  );
}
