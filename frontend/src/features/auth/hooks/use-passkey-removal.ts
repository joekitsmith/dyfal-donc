import { useState } from "react";

import type { Passkey } from "../types";

/** Removing a passkey is asked about first, naming the one chosen. */
export function usePasskeyRemoval(remove: (passkeyId: string) => void) {
  const [asking, setAsking] = useState<null | Passkey>(null);

  return {
    ask: (passkey: Passkey) => {
      setAsking(passkey);
    },
    asking,
    cancel: () => {
      setAsking(null);
    },
    confirm: () => {
      if (asking !== null) {
        remove(asking.id);
        setAsking(null);
      }
    },
  };
}
