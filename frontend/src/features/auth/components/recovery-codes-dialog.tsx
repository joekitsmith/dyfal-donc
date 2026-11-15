import Button from "@mui/material/Button";
import Checkbox from "@mui/material/Checkbox";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogTitle from "@mui/material/DialogTitle";
import FormControlLabel from "@mui/material/FormControlLabel";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import Stack from "@mui/material/Stack";

import { useRecoveryCodesDialog } from "../hooks/use-recovery-codes-dialog";

/** Shows new recovery codes once. It cannot be closed until the person says they have saved them. */
export function RecoveryCodesDialog() {
  const { codes, copy, done, download, open, saved } = useRecoveryCodesDialog();

  return (
    <Dialog open={open}>
      <DialogTitle>Save your recovery codes</DialogTitle>
      <DialogContent>
        <DialogContentText>
          If you lose your passkey, each of these gets you back into your account once. They are shown only now, so keep
          them somewhere safe.
        </DialogContentText>
        <List aria-label="Recovery codes" sx={{ fontFamily: "monospace" }}>
          {codes.map((code) => (
            <ListItem disablePadding key={code}>
              {code}
            </ListItem>
          ))}
        </List>
        <Stack direction="row" spacing={1}>
          <Button onClick={copy.onClick} variant="outlined">
            {copy.copied ? "Copied" : "Copy"}
          </Button>
          <Button onClick={download} variant="outlined">
            Download
          </Button>
        </Stack>
        <FormControlLabel
          control={
            <Checkbox
              checked={saved.checked}
              onChange={(event) => {
                saved.onChange(event.target.checked);
              }}
            />
          }
          label="I have saved these codes"
        />
      </DialogContent>
      <DialogActions>
        <Button disabled={done.disabled} onClick={done.onClick} variant="contained">
          Done
        </Button>
      </DialogActions>
    </Dialog>
  );
}
