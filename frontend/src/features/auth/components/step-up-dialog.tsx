import Box from "@mui/material/Box";

import { textStyle } from "@/theme/text-style";

import { useStepUpDialog } from "../hooks/use-step-up-dialog";
import { ConfirmDialog } from "./confirm-dialog";

/** Asks for a passkey before something that changes the account, so a stolen session cannot do it. */
export function StepUpDialog() {
  const { cancel, confirm, failure, open, text } = useStepUpDialog();

  return (
    <ConfirmDialog
      buttons={[
        {
          emphasis: "primary",
          hint: "Your device will ask you to confirm.",
          label: "Continue",
          onClick: confirm.onClick,
          unavailable: confirm.disabled,
        },
        { emphasis: "ghost", label: "Cancel", onClick: cancel },
      ]}
      description={text}
      notice={
        failure === null ? undefined : (
          <Box role="alert" sx={{ ...textStyle("body"), fontWeight: 500 }}>
            {failure}
          </Box>
        )
      }
      onClose={cancel}
      open={open}
      title="Confirm it's you"
    />
  );
}
