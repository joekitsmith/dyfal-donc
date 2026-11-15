import Button from "@mui/material/Button";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogTitle from "@mui/material/DialogTitle";

type ConfirmDialogProps = {
  readonly confirm: { readonly label: string; readonly onClick: () => void };
  readonly description: string;
  readonly onClose: () => void;
  readonly open: boolean;
  readonly title: string;
};

export function ConfirmDialog({ confirm, description, onClose, open, title }: ConfirmDialogProps) {
  return (
    <Dialog onClose={onClose} open={open}>
      <DialogTitle>{title}</DialogTitle>
      <DialogContent>
        <DialogContentText>{description}</DialogContentText>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button color="error" onClick={confirm.onClick}>
          {confirm.label}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
