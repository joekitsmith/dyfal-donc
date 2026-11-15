import Alert from "@mui/material/Alert";
import Button from "@mui/material/Button";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import MenuItem from "@mui/material/MenuItem";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { Controller } from "react-hook-form";

import { useReplayClip } from "@/hooks/use-replay-clip";

import type { ReportSource, ReportSubject } from "../types";

import { CATEGORY_OPTIONS } from "../constants";
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
  const { control, failure, isSending, onSubmit, sent, subject } = useReportForm({ allowNone, source, subjects });
  const { failed: audioFailed, play } = useReplayClip();

  if (sent) {
    return (
      <>
        <DialogContent>
          <Typography role="status">Thanks, it&apos;s been sent</Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose}>Close</Button>
        </DialogActions>
      </>
    );
  }

  return (
    <form
      noValidate
      onSubmit={(event) => {
        void onSubmit(event);
      }}
    >
      <DialogContent>
        <Stack spacing={2} sx={{ pt: 1 }}>
          {subject.fixed === undefined ? null : <SubjectSummary onPlay={play} subject={subject.fixed} />}
          {subject.choices.length === 0 ? null : (
            <SubjectChoice choices={subject.choices} control={control} onPlay={play} showNone={subject.showNone} />
          )}
          {audioFailed ? <Alert severity="error">The audio could not be played</Alert> : null}
          <Controller
            control={control}
            name="category"
            render={({ field, fieldState }) => (
              <TextField
                error={fieldState.error !== undefined}
                helperText={fieldState.error?.message}
                label="What kind of problem is it?"
                required
                select
                {...field}
              >
                {CATEGORY_OPTIONS.map((option) => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </TextField>
            )}
          />
          <Controller
            control={control}
            name="description"
            render={({ field, fieldState }) => (
              <TextField
                error={fieldState.error !== undefined}
                helperText={fieldState.error?.message}
                label="What is wrong?"
                minRows={3}
                multiline
                required
                {...field}
              />
            )}
          />
          {failure === null ? null : <Alert severity="error">{failure}</Alert>}
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button disabled={isSending} type="submit" variant="contained">
          {failure === null ? "Send" : "Try again"}
        </Button>
      </DialogActions>
    </form>
  );
}
