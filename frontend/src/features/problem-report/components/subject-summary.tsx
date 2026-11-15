import Stack from "@mui/material/Stack";

import type { ReportSubject } from "../types";

import { PlaySubjectButton } from "./play-subject-button";
import { SubjectText } from "./subject-text";

type SubjectSummaryProps = {
  readonly onPlay: (path: string) => void;
  readonly subject: ReportSubject;
};

/** What is being reported when there is nothing to choose between, with the Welsh to play. */
export function SubjectSummary({ onPlay, subject }: SubjectSummaryProps) {
  return (
    <Stack spacing={0.5}>
      <SubjectText subject={subject} />
      <PlaySubjectButton onPlay={onPlay} subject={subject} />
    </Stack>
  );
}
