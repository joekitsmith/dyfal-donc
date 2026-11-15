import Button from "@mui/material/Button";
import ListItem from "@mui/material/ListItem";
import ListItemText from "@mui/material/ListItemText";

import type { Passkey } from "../types";

export function PasskeyListItem({
  onRemove,
  passkey,
  removable,
}: {
  readonly onRemove: (passkeyId: string) => void;
  readonly passkey: Passkey;
  readonly removable: boolean;
}) {
  const added = new Date(passkey.createdAt).toLocaleDateString();
  const used =
    passkey.lastUsedAt === null ? "never used" : `last used ${new Date(passkey.lastUsedAt).toLocaleDateString()}`;

  return (
    <ListItem
      disableGutters
      secondaryAction={
        removable ? (
          <Button
            aria-label={`Remove ${passkey.label}`}
            color="error"
            onClick={() => {
              onRemove(passkey.id);
            }}
          >
            Remove
          </Button>
        ) : null
      }
    >
      <ListItemText primary={passkey.label} secondary={`Added ${added}, ${used}`} />
    </ListItem>
  );
}
