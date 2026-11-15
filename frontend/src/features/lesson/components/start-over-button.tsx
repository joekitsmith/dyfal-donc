import Button from "@mui/material/Button";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogTitle from "@mui/material/DialogTitle";
import { useState } from "react";

export function StartOverButton({ onConfirm }: { readonly onConfirm: () => void }) {
  const [open, setOpen] = useState(false);

  return (
    <>
      <Button
        onClick={() => {
          setOpen(true);
        }}
        variant="text"
      >
        Start over
      </Button>
      <Dialog
        onClose={() => {
          setOpen(false);
        }}
        open={open}
      >
        <DialogTitle>Start over?</DialogTitle>
        <DialogContent>
          <DialogContentText>
            This begins a new learner. Your current progress will no longer be shown.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => {
              setOpen(false);
            }}
          >
            Cancel
          </Button>
          <Button
            color="error"
            onClick={() => {
              setOpen(false);
              onConfirm();
            }}
          >
            Start over
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
