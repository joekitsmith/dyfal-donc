import List from "@mui/material/List";
import Typography from "@mui/material/Typography";

import type { Passkey } from "../types";

import { PasskeyListItem } from "./passkey-list-item";

/** The last passkey cannot be removed: it is the only way back in. */
export function PasskeyList({
  onRemove,
  passkeys,
}: {
  readonly onRemove: (passkeyId: string) => void;
  readonly passkeys: readonly Passkey[];
}) {
  if (passkeys.length === 0) {
    return <Typography color="text.secondary">No passkeys yet.</Typography>;
  }

  return (
    <List aria-label="Passkeys" disablePadding>
      {passkeys.map((passkey) => (
        <PasskeyListItem key={passkey.id} onRemove={onRemove} passkey={passkey} removable={passkeys.length > 1} />
      ))}
    </List>
  );
}
