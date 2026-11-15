import Button from "@mui/material/Button";

import { useDisclosure } from "@/hooks/use-disclosure";

import { ConfirmDialog } from "./confirm-dialog";

type SignOutButtonProps = {
  readonly isGuest: boolean;
  readonly onSignOut: () => void;
};

/** A guest has no passkey to sign back in with, so signing out is confirmed first. */
export function SignOutButton({ isGuest, onSignOut }: SignOutButtonProps) {
  const dialog = useDisclosure();

  return (
    <>
      <Button onClick={isGuest ? dialog.open : onSignOut} variant="outlined">
        Sign out
      </Button>
      <ConfirmDialog
        confirm={{ label: "Sign out", onClick: onSignOut }}
        description="You are a guest, so there is no way back in. Add a passkey first if you want to keep your progress."
        onClose={dialog.close}
        open={dialog.isOpen}
        title="Sign out as a guest?"
      />
    </>
  );
}
