import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";

import type { ReportSubject } from "../types";

type SubjectTextProps = { readonly subject: ReportSubject };

export function SubjectText({ subject }: SubjectTextProps) {
  return (
    <Stack>
      <Typography>{subject.english}</Typography>
      <Typography>{subject.welsh}</Typography>
    </Stack>
  );
}
