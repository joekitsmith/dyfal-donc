import type { Passkey } from "../types";

import { passkeyName } from "../utils/describe-passkey";
import { ConfirmDialog } from "./confirm-dialog";

type RemovePasskeyDialogProps = {
  /** The passkey being asked about. Without one the dialog is closed. */
  readonly asking: null | Passkey;
  readonly onCancel: () => void;
  readonly onConfirm: () => void;
};

export function RemovePasskeyDialog({ asking, onCancel, onConfirm }: RemovePasskeyDialogProps) {
  return (
    <ConfirmDialog
      buttons={[
        { emphasis: "primary", label: "Remove", onClick: onConfirm },
        { emphasis: "ghost", label: "Cancel", onClick: onCancel },
      ]}
      description="You won't be able to sign in with it any more."
      onClose={onCancel}
      open={asking !== null}
      title={`Remove "${asking === null ? "" : passkeyName(asking)}"?`}
    />
  );
}
