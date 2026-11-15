import {
  type PublicKeyCredentialCreationOptionsJSON,
  type PublicKeyCredentialRequestOptionsJSON,
  startAuthentication,
  startRegistration,
} from "@simplewebauthn/browser";

import type { ApiClient } from "@/api/client";

import { unwrap } from "@/api/api-error";

import type { RegisteredPasskey, SessionUser } from "../types";

import { toPasskey, toSessionUser } from "./auth-requests";
import { withStepUp } from "./with-step-up";

/** Adds a passkey for whoever is signed in. The browser asks the person to approve it. */
export async function registerPasskey(client: ApiClient, label: string | undefined): Promise<RegisteredPasskey> {
  return withStepUp(async () => {
    const options = unwrap(await client.POST("/auth/passkeys/registration/options"));
    const credential = await startRegistration({ optionsJSON: asCreationOptions(options) });
    const registered = unwrap(
      await client.POST("/auth/passkeys/registration/verify", {
        body: { credential: { ...credential }, label: label ?? null },
      }),
    );

    return { passkey: toPasskey(registered.passkey), recoveryCodes: registered.recovery_codes ?? null };
  });
}

/** Signs in with any passkey the browser holds for this site. */
export async function signInWithPasskey(client: ApiClient): Promise<SessionUser> {
  const options = unwrap(await client.POST("/auth/passkeys/authentication/options"));
  const credential = await startAuthentication({ optionsJSON: asRequestOptions(options) });

  return toSessionUser(
    unwrap(await client.POST("/auth/passkeys/authentication/verify", { body: { credential: { ...credential } } })),
  );
}

// The API types WebAuthn's JSON as a free-form object. The server makes exactly the JSON
// that the browser library takes, so these two assertions are the only place that is claimed.
function asCreationOptions(options: object): PublicKeyCredentialCreationOptionsJSON {
  return options as PublicKeyCredentialCreationOptionsJSON;
}

function asRequestOptions(options: object): PublicKeyCredentialRequestOptionsJSON {
  return options as PublicKeyCredentialRequestOptionsJSON;
}
