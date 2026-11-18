import { useEffect, useSyncExternalStore } from "react";

import {
  hasSwitchedAccount,
  leaveAccountScreen,
  stayOnAccountScreen,
  subscribeToConfirmation,
} from "../stores/step-up-store";

/** Whether to tell the person that confirming signed them in to a different account. It is said once, while they are on the account screen. */
export function useAccountSwitchedNotice(): boolean {
  const visible = useSyncExternalStore(subscribeToConfirmation, hasSwitchedAccount, () => false);

  useEffect(() => {
    stayOnAccountScreen();

    return leaveAccountScreen;
  }, []);

  return visible;
}
