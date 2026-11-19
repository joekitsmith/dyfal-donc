import Box from "@mui/material/Box";
import { type Control, Controller } from "react-hook-form";

import { ChoiceRow } from "@/components/choice-row";
import { textStyle } from "@/theme/text-style";

import type { ReportFormValues, ReportSubject } from "../types";

import { NO_SUBJECT, NO_SUBJECT_LABEL, SUBJECT_LEGEND } from "../constants";
import { SubjectRow } from "./subject-row";
import { SubjectText } from "./subject-text";

type SubjectChoiceProps = {
  readonly choices: readonly ReportSubject[];
  readonly clip: { readonly failed: null | string; readonly playing: null | string };
  readonly control: Control<ReportFormValues>;
  readonly onPlay: (path: string) => void;
  readonly showNone: boolean;
};

const RULE = "1px solid color-mix(in srgb, var(--dd-line) 35%, transparent)";

/** Which of the sentences the report is about, or none of them. */
export function SubjectChoice({ choices, clip, control, onPlay, showNone }: SubjectChoiceProps) {
  return (
    <Controller
      control={control}
      name="subjectId"
      render={({ field }) => (
        <Box component="fieldset" sx={{ border: 0, m: 0, minWidth: 0, p: 0 }}>
          <Box component="legend" sx={{ ...textStyle("label"), fontWeight: 600, mb: "8px", p: 0 }}>
            {SUBJECT_LEGEND}
          </Box>
          <Box
            sx={{
              "& > div + div": { borderTop: RULE },
              backgroundColor: "var(--dd-ground)",
              borderRadius: "10px",
              p: "0 16px",
            }}
          >
            {choices.map((subject) => (
              <SubjectRow
                failed={clip.failed !== null && clip.failed === subject.audio}
                key={subject.id}
                leading={
                  <ChoiceRow
                    checked={field.value === subject.id}
                    label={<SubjectText subject={subject} />}
                    name="report-subject"
                    onChange={() => {
                      field.onChange(subject.id);
                    }}
                    type="radio"
                    value={subject.id}
                  />
                }
                onPlay={onPlay}
                playing={clip.playing !== null && clip.playing === subject.audio}
                subject={subject}
              />
            ))}
            {showNone ? (
              <Box>
                <ChoiceRow
                  checked={field.value === NO_SUBJECT}
                  label={NO_SUBJECT_LABEL}
                  name="report-subject"
                  onChange={() => {
                    field.onChange(NO_SUBJECT);
                  }}
                  type="radio"
                  value={NO_SUBJECT}
                />
              </Box>
            ) : null}
          </Box>
        </Box>
      )}
    />
  );
}
