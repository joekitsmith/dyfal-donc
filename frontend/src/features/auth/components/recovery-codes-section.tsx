import Alert from "@mui/material/Alert";
import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";

import { useDisclosure } from "@/hooks/use-disclosure";

import { useRecoveryCodesSection } from "../hooks/use-recovery-codes-section";
import { ConfirmDialog } from "./confirm-dialog";

export function RecoveryCodesSection() {
  const { failed, generate, isGenerating, isLoading, low, remaining } = useRecoveryCodesSection();
  const dialog = useDisclosure();

  if (isLoading) {
    return null;
  }

  return (
    <Stack component="section" spacing={1}>
      <Typography component="h2" variant="h6">
        Recovery codes
      </Typography>
      <Typography>
        Each code gets you back in once if you lose your passkey.{" "}
        {remaining === undefined ? "" : `${remaining} unused.`}
      </Typography>
      {low ? (
        <Alert severity="warning">
          {remaining === 0 ? "You have no recovery codes left." : "You are running low on recovery codes."} Make a new
          set to be safe.
        </Alert>
      ) : null}
      {failed ? <Alert severity="error">Something went wrong. Try again.</Alert> : null}
      <Button disabled={isGenerating} onClick={dialog.open} sx={{ alignSelf: "flex-start" }} variant="outlined">
        Make new codes
      </Button>
      <ConfirmDialog
        buttons={[
          {
            emphasis: "primary",
            label: "Make new codes",
            onClick: () => {
              dialog.close();
              generate();
            },
          },
          { emphasis: "ghost", label: "Cancel", onClick: dialog.close },
        ]}
        description="Your current codes will stop working."
        onClose={dialog.close}
        open={dialog.isOpen}
        title="Make new recovery codes?"
      />
    </Stack>
  );
}
