import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";

import type { ReportSource, ReportSubject } from "../types";

import { ReportForm } from "./report-form";

type ReportDialogProps = {
  /** Adds "Not about one of these sentences" to the choice, for a report that is about none of them. */
  readonly allowNone: boolean;
  readonly onClose: () => void;
  readonly open: boolean;
  readonly source: ReportSource;
  readonly subjects: readonly ReportSubject[];
};

/** Tells the developer that something is wrong, from wherever the learner noticed it. */
export function ReportDialog({ allowNone, onClose, open, source, subjects }: ReportDialogProps) {
  return (
    <Dialog fullWidth maxWidth="sm" onClose={onClose} open={open}>
      <DialogTitle>Report a problem</DialogTitle>
      <ReportForm allowNone={allowNone} onClose={onClose} source={source} subjects={subjects} />
    </Dialog>
  );
}
