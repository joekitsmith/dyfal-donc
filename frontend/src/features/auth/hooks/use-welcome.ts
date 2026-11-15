import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { ROUTES } from "@/config/paths";

import type { PasskeyFailure } from "../types";

import { useSession } from "../api/use-session";
import { useSignInWithPasskey } from "../api/use-sign-in-with-passkey";
import { useStartGuest } from "../api/use-start-guest";
import { passkeyFailure } from "../utils/passkey-failure";
import { usePasskeySupport } from "./use-passkey-support";

/** What the welcome screen does: start as a guest or sign in, and move on once someone is signed in. */
export function useWelcome() {
  const router = useRouter();
  const session = useSession();
  const guest = useStartGuest();
  const signIn = useSignInWithPasskey();
  const supported = usePasskeySupport();
  const signedIn = session.data !== undefined && session.data !== null;

  useEffect(() => {
    if (signedIn) {
      router.replace(ROUTES.learn);
    }
  }, [router, signedIn]);

  const failure: null | PasskeyFailure = signIn.isError
    ? passkeyFailure(signIn.error)
    : guest.isError
      ? "other"
      : supported
        ? null
        : "unsupported";

  return {
    busy: guest.isPending || signIn.isPending || signedIn,
    failure,
    isLoading: session.isPending,
    signIn: signIn.mutate,
    startGuest: guest.mutate,
    supported,
  };
}
