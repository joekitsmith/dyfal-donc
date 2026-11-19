import Box from "@mui/material/Box";

import { textStyle } from "@/theme/text-style";

import type { ReportSubject } from "../types";

import { PlaySubjectButton } from "./play-subject-button";
import { SubjectText } from "./subject-text";

type SubjectRowProps = {
  /** Whether the clip failed lately, which is said under the row. */
  readonly failed: boolean;
  /** Sits beside the text. In a choice it is the radio, and then it is also what is pressed to choose. */
  readonly leading?: React.ReactNode;
  readonly onPlay: (path: string) => void;
  readonly playing: boolean;
  readonly subject: ReportSubject;
};

/** A sentence, word or phrase being reported, with its Welsh to play. */
export function SubjectRow({ failed, leading, onPlay, playing, subject }: SubjectRowProps) {
  return (
    <Box>
      <Box sx={{ alignItems: "center", display: "flex", gap: "8px", justifyContent: "space-between", minHeight: 56 }}>
        {leading ?? <SubjectText subject={subject} />}
        <PlaySubjectButton onPlay={onPlay} playing={playing} subject={subject} />
      </Box>
      {failed ? (
        <Box role="status" sx={{ ...textStyle("hint"), color: "var(--dd-muted)", pb: "8px" }}>
          That couldn&apos;t be played.
        </Box>
      ) : null}
    </Box>
  );
}
