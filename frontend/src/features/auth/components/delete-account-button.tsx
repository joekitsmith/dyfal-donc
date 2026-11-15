import Button from "@mui/material/Button";

import { useDisclosure } from "@/hooks/use-disclosure";

import { ConfirmDialog } from "./confirm-dialog";

type DeleteAccountButtonProps = {
  readonly onDelete: () => void;
};

export function DeleteAccountButton({ onDelete }: DeleteAccountButtonProps) {
  const dialog = useDisclosure();

  return (
    <>
      <Button color="error" onClick={dialog.open} variant="text">
        Delete account
      </Button>
      <ConfirmDialog
        confirm={{ label: "Delete everything", onClick: onDelete }}
        description="This deletes your account, your passkeys and all your progress. It cannot be undone."
        onClose={dialog.close}
        open={dialog.isOpen}
        title="Delete your account?"
      />
    </>
  );
}
