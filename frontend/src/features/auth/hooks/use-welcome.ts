import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { ROUTES } from "@/config/paths";

import type { PasskeyFailure } from "../types";

import { useSession } from "../api/use-session";
import { useSignInWithPasskey } from "../api/use-sign-in-with-passkey";
import { useStartGuest } from "../api/use-start-guest";
import { WELCOME_NOTICES } from "../constants";
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
      router.replace(ROUTES.home);
    }
  }, [router, signedIn]);

  const notice = welcomeNotice(
    signIn.isError ? passkeyFailure(signIn.error) : guest.isError ? "other" : supported ? null : "unsupported",
  );

  const disabled = guest.isPending || signIn.isPending || signedIn;

  return {
    isLoading: session.isPending,
    notice,
    signIn: {
      disabled,
      onClick: () => {
        signIn.mutate();
      },
      supported,
    },
    tryIt: {
      disabled,
      onClick: () => {
        guest.mutate();
      },
    },
  };
}

function welcomeNotice(failure: null | PasskeyFailure): null | string {
  if (failure === null) {
    return null;
  }

  // Signing in never meets a passkey that is already registered, so that reads as any other failure
  return WELCOME_NOTICES[failure === "already_registered" ? "other" : failure];
}
