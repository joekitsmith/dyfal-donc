import Button from "@mui/material/Button";
import { useState } from "react";

import { ConfirmDialog } from "./confirm-dialog";

export function DeleteAccountButton({ onDelete }: { readonly onDelete: () => void }) {
  const [open, setOpen] = useState(false);

  return (
    <>
      <Button
        color="error"
        onClick={() => {
          setOpen(true);
        }}
        variant="text"
      >
        Delete account
      </Button>
      <ConfirmDialog
        confirmLabel="Delete everything"
        description="This deletes your account, your passkeys and all your progress. It cannot be undone."
        onCancel={() => {
          setOpen(false);
        }}
        onConfirm={onDelete}
        open={open}
        title="Delete your account?"
      />
    </>
  );
}
