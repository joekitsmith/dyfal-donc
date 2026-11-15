import FormControl from "@mui/material/FormControl";
import FormControlLabel from "@mui/material/FormControlLabel";
import FormLabel from "@mui/material/FormLabel";
import Radio from "@mui/material/Radio";
import RadioGroup from "@mui/material/RadioGroup";
import Stack from "@mui/material/Stack";
import { type Control, Controller } from "react-hook-form";

import type { ReportFormValues, ReportSubject } from "../types";

import { NO_SUBJECT, NO_SUBJECT_LABEL } from "../constants";
import { PlaySubjectButton } from "./play-subject-button";
import { SubjectText } from "./subject-text";

type SubjectChoiceProps = {
  readonly choices: readonly ReportSubject[];
  readonly control: Control<ReportFormValues>;
  readonly onPlay: (path: string) => void;
  readonly showNone: boolean;
};

/** Which of the sentences the report is about, or none of them. */
export function SubjectChoice({ choices, control, onPlay, showNone }: SubjectChoiceProps) {
  return (
    <Controller
      control={control}
      name="subjectId"
      render={({ field }) => (
        <FormControl>
          <FormLabel id="report-subject-label">What is the problem with?</FormLabel>
          <RadioGroup aria-labelledby="report-subject-label" {...field}>
            {choices.map((subject) => (
              <Stack direction="row" key={subject.id} spacing={1} sx={{ alignItems: "center" }}>
                <FormControlLabel control={<Radio />} label={<SubjectText subject={subject} />} value={subject.id} />
                <PlaySubjectButton onPlay={onPlay} subject={subject} />
              </Stack>
            ))}
            {showNone ? <FormControlLabel control={<Radio />} label={NO_SUBJECT_LABEL} value={NO_SUBJECT} /> : null}
          </RadioGroup>
        </FormControl>
      )}
    />
  );
}
