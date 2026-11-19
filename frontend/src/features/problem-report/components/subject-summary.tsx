import Box from "@mui/material/Box";

import type { ReportSubject } from "../types";

import { SubjectRow } from "./subject-row";

type SubjectSummaryProps = {
  readonly failed: boolean;
  readonly onPlay: (path: string) => void;
  readonly playing: boolean;
  readonly subject: ReportSubject;
};

/** What is being reported when there is nothing to choose between, with the Welsh to play. */
export function SubjectSummary({ failed, onPlay, playing, subject }: SubjectSummaryProps) {
  return (
    <Box sx={{ backgroundColor: "var(--dd-ground)", borderRadius: "10px", p: "4px 16px" }}>
      <SubjectRow failed={failed} onPlay={onPlay} playing={playing} subject={subject} />
    </Box>
  );
}
