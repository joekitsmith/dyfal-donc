import Alert from "@mui/material/Alert";
import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";

import { useSaveProgress } from "../hooks/use-save-progress";
import { PasskeyFailureAlert } from "./passkey-failure-alert";

/**
 * Progress is already saved on the server as you go. A passkey is what lets you get back to it from
 * anywhere, and without one a guest only has this browser.
 */
type SaveProgressPromptProps = {
  readonly onDismiss?: () => void;
  readonly onSaved?: () => void;
};

export function SaveProgressPrompt({ onDismiss, onSaved }: SaveProgressPromptProps) {
  const { failure, isSaving, save } = useSaveProgress(onSaved);

  return (
    <Stack spacing={1}>
      <Alert
        action={
          <Stack direction="row" spacing={1}>
            <Button
              color="inherit"
              disabled={isSaving}
              onClick={() => {
                save();
              }}
              variant="outlined"
            >
              Add a passkey
            </Button>
            {onDismiss ? (
              <Button color="inherit" onClick={onDismiss}>
                Not now
              </Button>
            ) : null}
          </Stack>
        }
        severity="info"
      >
        Your progress is saved on this browser. Add a passkey to sign in from anywhere and keep it for good.
      </Alert>
      {failure ? <PasskeyFailureAlert failure={failure} /> : null}
    </Stack>
  );
}
