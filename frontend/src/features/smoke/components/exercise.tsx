import Alert from "@mui/material/Alert";
import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";

import { useNextExercise } from "../api/use-next-exercise";
import { ClipButton } from "./clip-button";

export function Exercise({ learnerId }: { readonly learnerId: string }) {
  const { error, fetchNext, isPending, outcome } = useNextExercise(learnerId);

  return (
    <Stack spacing={2} sx={{ maxWidth: 480, mx: "auto", p: 2 }}>
      <Button disabled={isPending} onClick={fetchNext} variant="contained">
        Start
      </Button>
      {error ? <Alert severity="error">The next exercise could not be loaded</Alert> : null}
      {outcome?.kind === "nothing_eligible" ? <Typography>Nothing to do: {outcome.reason}</Typography> : null}
      {outcome?.kind === "exercise" ? (
        <>
          <Typography>{outcome.english}</Typography>
          <Typography>{outcome.welsh}</Typography>
          <ClipButton label="English" path={outcome.audio.english} />
          <ClipButton label="Welsh" path={outcome.audio.welsh} />
          <ClipButton label="Welsh, slow" path={outcome.audio.welsh_slow} />
        </>
      ) : null}
    </Stack>
  );
}
