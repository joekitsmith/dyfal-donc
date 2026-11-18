import { TextButton } from "@/components/text-button";
import { useDisclosure } from "@/hooks/use-disclosure";

import { ConfirmDialog } from "./confirm-dialog";

type DeleteAccountButtonProps = {
  readonly onDelete: () => void;
};

export function DeleteAccountButton({ onDelete }: DeleteAccountButtonProps) {
  const dialog = useDisclosure();

  return (
    <>
      <TextButton centred onClick={dialog.open}>
        Delete account
      </TextButton>
      <ConfirmDialog
        buttons={[
          { emphasis: "primary", label: "Delete account", onClick: onDelete },
          { emphasis: "ghost", label: "Cancel", onClick: dialog.close },
        ]}
        description="This deletes your account, your passkeys, all your progress and any problem reports you sent. It cannot be undone."
        onClose={dialog.close}
        open={dialog.isOpen}
        title="Delete your account?"
      />
    </>
  );
}
