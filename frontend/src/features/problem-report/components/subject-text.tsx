import Box from "@mui/material/Box";

import { textStyle } from "@/theme/text-style";

import type { ReportSubject } from "../types";

type SubjectTextProps = { readonly subject: ReportSubject };

/** The Welsh over the English. */
export function SubjectText({ subject }: SubjectTextProps) {
  return (
    <Box>
      <Box lang="cy" sx={{ ...textStyle("label"), fontWeight: 600 }}>
        {subject.welsh}
      </Box>
      <Box sx={{ ...textStyle("hint"), color: "var(--dd-muted)" }}>{subject.english}</Box>
    </Box>
  );
}
