import Button from "@mui/material/Button";

import type { ReportSubject } from "../types";

type PlaySubjectButtonProps = {
  readonly onPlay: (path: string) => void;
  readonly subject: ReportSubject;
};

/** Plays the subject's Welsh. It shows nothing for a subject with no audio. */
export function PlaySubjectButton({ onPlay, subject }: PlaySubjectButtonProps) {
  const { audio } = subject;

  if (audio === null) {
    return null;
  }

  return (
    <Button
      aria-label={`Play ${subject.welsh}`}
      onClick={() => {
        onPlay(audio);
      }}
      size="small"
      sx={{ alignSelf: "flex-start" }}
      variant="outlined"
    >
      Play
    </Button>
  );
}
