import { ListCard } from "@/components/list-card";

import type { Passkey } from "../types";

import { usePasskeyRemoval } from "../hooks/use-passkey-removal";
import { PasskeyListItem } from "./passkey-list-item";
import { RemovePasskeyDialog } from "./remove-passkey-dialog";

/** The last passkey cannot be removed: it is the only way back in. */
type PasskeyListProps = {
  readonly onRemove: (passkeyId: string) => void;
  readonly passkeys: readonly Passkey[];
};

export function PasskeyList({ onRemove, passkeys }: PasskeyListProps) {
  const removal = usePasskeyRemoval(onRemove);

  return (
    <>
      <ListCard label="Passkeys">
        {passkeys.map((passkey) => (
          <PasskeyListItem
            key={passkey.id}
            onRemove={() => {
              removal.ask(passkey);
            }}
            passkey={passkey}
            removable={passkeys.length > 1}
          />
        ))}
      </ListCard>
      <RemovePasskeyDialog asking={removal.asking} onCancel={removal.cancel} onConfirm={removal.confirm} />
    </>
  );
}
