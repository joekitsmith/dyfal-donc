import Button from "@mui/material/Button";
import { useState } from "react";

import { ConfirmDialog } from "./confirm-dialog";

/** A guest has no passkey to sign back in with, so signing out is confirmed first. */
export function SignOutButton({ isGuest, onSignOut }: { readonly isGuest: boolean; readonly onSignOut: () => void }) {
  const [open, setOpen] = useState(false);

  return (
    <>
      <Button
        onClick={() => {
          if (isGuest) {
            setOpen(true);
          } else {
            onSignOut();
          }
        }}
        variant="outlined"
      >
        Sign out
      </Button>
      <ConfirmDialog
        confirmLabel="Sign out"
        description="You are a guest, so there is no way back in. Add a passkey first if you want to keep your progress."
        onCancel={() => {
          setOpen(false);
        }}
        onConfirm={onSignOut}
        open={open}
        title="Sign out as a guest?"
      />
    </>
  );
}
