import Button from "@mui/material/Button";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogTitle from "@mui/material/DialogTitle";

import { useStepUpDialog } from "../hooks/use-step-up-dialog";
import { PasskeyFailureAlert } from "./passkey-failure-alert";

/** Asks for a passkey before something that changes the account, so a stolen session cannot do it. */
export function StepUpDialog() {
  const { cancel, confirm, failure, open } = useStepUpDialog();

  return (
    <Dialog onClose={cancel} open={open}>
      <DialogTitle>Confirm it is you</DialogTitle>
      <DialogContent>
        <DialogContentText>
          For your security, confirm with your passkey before changing your account.
        </DialogContentText>
        {failure ? <PasskeyFailureAlert failure={failure} /> : null}
      </DialogContent>
      <DialogActions>
        <Button onClick={cancel}>Cancel</Button>
        <Button disabled={confirm.disabled} onClick={confirm.onClick} variant="contained">
          Confirm with passkey
        </Button>
      </DialogActions>
    </Dialog>
  );
}
