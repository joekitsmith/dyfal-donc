import Button from "@mui/material/Button";
import ListItem from "@mui/material/ListItem";
import ListItemText from "@mui/material/ListItemText";

import type { Passkey } from "../types";

import { describePasskey } from "../utils/describe-passkey";

type PasskeyListItemProps = {
  readonly onRemove: () => void;
  readonly passkey: Passkey;
  readonly removable: boolean;
};

export function PasskeyListItem({ onRemove, passkey, removable }: PasskeyListItemProps) {
  return (
    <ListItem
      disableGutters
      secondaryAction={
        removable ? (
          <Button aria-label={`Remove ${passkey.label}`} onClick={onRemove}>
            Remove
          </Button>
        ) : null
      }
    >
      <ListItemText primary={passkey.label} secondary={describePasskey(passkey)} />
    </ListItem>
  );
}
