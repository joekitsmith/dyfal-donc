import Box from "@mui/material/Box";

import { Button } from "@/components/button";
import { NoticeCard } from "@/components/notice-card";

import { useSaveProgress } from "../hooks/use-save-progress";
import { PasskeyFailureNotice } from "./passkey-failure-notice";

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
    <Box sx={{ display: "flex", flexDirection: "column", gap: "12px" }}>
      <NoticeCard
        actions={
          <>
            <Button
              compact
              onClick={() => {
                save();
              }}
              unavailable={isSaving}
              variant="primary"
            >
              Add a passkey
            </Button>
            {onDismiss ? (
              <Button onClick={onDismiss} variant="ghost">
                Not now
              </Button>
            ) : null}
          </>
        }
        hint="Your device will ask you to confirm."
      >
        Your progress is saved on this browser. Add a passkey to get back in from any device.
      </NoticeCard>
      {failure ? <PasskeyFailureNotice failure={failure} /> : null}
    </Box>
  );
}
