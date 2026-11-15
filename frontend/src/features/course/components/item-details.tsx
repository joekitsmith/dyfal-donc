import Alert from "@mui/material/Alert";
import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";

import type { ItemDetail } from "../types";

import { formatFirstMet } from "../utils/format-first-met";

type ItemDetailsProps = {
  readonly item: ItemDetail;
  readonly playback: {
    readonly failed: boolean;
    readonly play: (() => void) | undefined;
  };
};

/** An item in both languages, how to hear it if it is a word, and what else is known about it. */
export function ItemDetails({ item, playback }: ItemDetailsProps) {
  return (
    <Stack spacing={1}>
      <Typography component="h1" variant="h4">
        {item.welsh}
      </Typography>
      <Typography>{item.english}</Typography>
      <Typography color="text.secondary">{item.kind === "word" ? "Word" : "Way of saying things"}</Typography>
      {item.kind === "phrase" ? <Typography>The part in [brackets] is where a word goes.</Typography> : null}
      {playback.play === undefined ? null : (
        <Button
          aria-label={`Play ${item.welsh}`}
          onClick={playback.play}
          sx={{ alignSelf: "flex-start" }}
          variant="outlined"
        >
          Play
        </Button>
      )}
      {playback.failed ? <Alert severity="error">The audio could not be played</Alert> : null}
      {item.forms.length > 0 ? <Typography>Other forms: {item.forms.join(", ")}</Typography> : null}
      {item.notes === "" ? null : <Typography>Notes: {item.notes}</Typography>}
      <Typography color="text.secondary">First met {formatFirstMet(item.first_met_at)}</Typography>
    </Stack>
  );
}
