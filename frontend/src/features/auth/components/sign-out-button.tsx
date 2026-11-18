import { Button } from "@/components/button";
import { useDisclosure } from "@/hooks/use-disclosure";

import { useSaveProgress } from "../hooks/use-save-progress";
import { ConfirmDialog } from "./confirm-dialog";
import { PasskeyFailureNotice } from "./passkey-failure-notice";

type SignOutButtonProps = {
  readonly isGuest: boolean;
  readonly onSignOut: () => void;
};

/** A guest has no passkey to sign back in with, so signing out is confirmed first, with a way to get one. */
export function SignOutButton({ isGuest, onSignOut }: SignOutButtonProps) {
  const dialog = useDisclosure();
  const { failure, isSaving, save } = useSaveProgress(dialog.close);

  return (
    <>
      <Button edge full onClick={isGuest ? dialog.open : onSignOut} tall variant="ghost">
        Sign out
      </Button>
      <ConfirmDialog
        buttons={[
          {
            emphasis: "primary",
            hint: "Your device will ask you to confirm.",
            label: "Add a passkey",
            onClick: () => {
              save();
            },
            unavailable: isSaving,
          },
          { emphasis: "edge", label: "Sign out anyway", onClick: onSignOut },
          { emphasis: "ghost", label: "Cancel", onClick: dialog.close },
        ]}
        description="There's no way back into a guest account. Add a passkey first if you want to keep your progress."
        notice={failure ? <PasskeyFailureNotice failure={failure} /> : undefined}
        onClose={dialog.close}
        open={dialog.isOpen}
        title="Sign out of this guest account?"
      />
    </>
  );
}
