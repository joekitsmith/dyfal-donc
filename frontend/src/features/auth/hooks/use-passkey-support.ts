import { browserSupportsWebAuthn } from "@simplewebauthn/browser";
import { useSyncExternalStore } from "react";

function subscribe(): () => void {
  return () => undefined;
}

/** Whether this browser can use passkeys. The server render assumes it can, and the browser corrects that. */
export function usePasskeySupport(): boolean {
  return useSyncExternalStore(subscribe, browserSupportsWebAuthn, () => true);
}
