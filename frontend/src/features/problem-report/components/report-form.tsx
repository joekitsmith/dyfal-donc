import Box from "@mui/material/Box";

import { Button } from "@/components/button";
import { TickIcon } from "@/components/icons/tick-icon";
import { SelectField } from "@/components/select-field";
import { TextField } from "@/components/text-field";
import { useReplayClip } from "@/hooks/use-replay-clip";
import { textStyle } from "@/theme/text-style";

import type { ReportSource, ReportSubject } from "../types";

import { CATEGORY_OPTIONS, DESCRIPTION_MAXIMUM_LENGTH } from "../constants";
import { useReportForm } from "../hooks/use-report-form";
import { SubjectChoice } from "./subject-choice";
import { SubjectSummary } from "./subject-summary";

type ReportFormProps = {
  readonly allowNone: boolean;
  readonly onClose: () => void;
  readonly source: ReportSource;
  readonly subjects: readonly ReportSubject[];
};

/** The report, then a thank-you once it is sent. It starts afresh each time it is mounted. */
export function ReportForm({ allowNone, onClose, source, subjects }: ReportFormProps) {
  const { control, description, errors, failure, isSending, onSubmit, register, sent, subject } = useReportForm({
    allowNone,
    source,
    subjects,
  });
  const { failed, play, playing } = useReplayClip();
  const fixed = subject.fixed;

  if (sent) {
    return (
      <Box sx={{ display: "flex", flex: 1, flexDirection: "column", minHeight: 0 }}>
        <Box
          role="status"
          sx={{ ...textStyle("title"), alignItems: "center", display: "flex", gap: "10px", mt: "24px" }}
        >
          <Box aria-hidden="true" sx={{ color: "var(--dd-accent)", display: "flex" }}>
            <TickIcon size={24} />
          </Box>
          Thanks, it&apos;s been sent
        </Box>
        <Box sx={{ flex: 1 }} />
        <Button onClick={onClose} variant="primary">
          Close
        </Button>
      </Box>
    );
  }

  return (
    <Box
      component="form"
      noValidate
      onSubmit={(event) => {
        void onSubmit(event);
      }}
      sx={{ display: "flex", flex: 1, flexDirection: "column", minHeight: 0 }}
    >
      <Box
        sx={{
          display: "flex",
          flex: 1,
          flexDirection: "column",
          gap: "20px",
          minHeight: 0,
          mt: "20px",
          overflowY: "auto",
          pb: "4px",
        }}
      >
        {fixed === undefined ? null : (
          <SubjectSummary
            failed={failed !== null && failed === fixed.audio}
            onPlay={play}
            playing={playing !== null && playing === fixed.audio}
            subject={fixed}
          />
        )}
        {subject.choices.length === 0 ? null : (
          <SubjectChoice
            choices={subject.choices}
            clip={{ failed, playing }}
            control={control}
            onPlay={play}
            showNone={subject.showNone}
          />
        )}
        <SelectField
          input={register("category")}
          label="What kind of problem is it?"
          message={errors.category}
          options={CATEGORY_OPTIONS}
          prompt="Choose one"
        />
        <TextField
          counter={`${description.length.toLocaleString("en-GB")} / ${DESCRIPTION_MAXIMUM_LENGTH.toLocaleString("en-GB")}`}
          input={register("description")}
          label="What is wrong?"
          message={errors.description}
          multiline={4}
        />
      </Box>
      <Box sx={{ pt: "16px" }}>
        {failure === null ? null : (
          <Box role="alert" sx={{ ...textStyle("body"), fontWeight: 500, mb: "12px" }}>
            {failure}
          </Box>
        )}
        <Box sx={{ display: "flex", gap: "12px" }}>
          <Box sx={{ flex: 1 }}>
            <Button edge full onClick={onClose} tall variant="ghost">
              Cancel
            </Button>
          </Box>
          <Box sx={{ flex: 1 }}>
            <Button type="submit" unavailable={isSending} variant="primary">
              {isSending ? "Sending…" : failure === null ? "Send" : "Try again"}
            </Button>
          </Box>
        </Box>
      </Box>
    </Box>
  );
}
