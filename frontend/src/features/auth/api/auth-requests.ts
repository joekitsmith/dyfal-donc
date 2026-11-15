import type { ApiClient } from "@/api/client";
import type { components } from "@/api/schema";

import { ApiError, assertOk, unwrap } from "@/api/api-error";

import type { Passkey, SessionUser } from "../types";

import { UNAUTHORIZED_STATUS } from "../constants";

export async function deleteAccount(client: ApiClient): Promise<void> {
  assertOk(await client.DELETE("/me"));
}

export async function listPasskeys(client: ApiClient): Promise<readonly Passkey[]> {
  return unwrap(await client.GET("/me/passkeys")).map(toPasskey);
}

export async function getRecoveryCodeStatus(client: ApiClient): Promise<number> {
  return unwrap(await client.GET("/me/recovery-codes")).remaining;
}

export async function removePasskey(client: ApiClient, passkeyId: string): Promise<void> {
  assertOk(await client.DELETE("/me/passkeys/{passkey_id}", { params: { path: { passkey_id: passkeyId } } }));
}

/** A new set of recovery codes, which replaces the old one and is shown only now. */
export async function replaceRecoveryCodes(client: ApiClient): Promise<readonly string[]> {
  return unwrap(await client.POST("/me/recovery-codes")).codes;
}

/** Whoever the session cookie says is signed in, or null when nobody is. */
export async function resolveSession(client: ApiClient): Promise<null | SessionUser> {
  const { data, response } = await client.GET("/me");

  if (data !== undefined) {
    return toSessionUser(data);
  }

  if (response.status === UNAUTHORIZED_STATUS) {
    return null;
  }

  throw new ApiError(response.status);
}

/** Signs in with a recovery code, which works once. */
export async function signInWithRecoveryCode(client: ApiClient, code: string): Promise<SessionUser> {
  return toSessionUser(unwrap(await client.POST("/auth/recovery/verify", { body: { code } })));
}

export async function signOut(client: ApiClient): Promise<void> {
  assertOk(await client.POST("/auth/logout"));
}

/** Starts straight away as a guest, so there is no sign-up in the way. */
export async function startGuest(client: ApiClient): Promise<SessionUser> {
  return toSessionUser(unwrap(await client.POST("/auth/guest")));
}

export function toPasskey(passkey: components["schemas"]["PasskeyResponse"]): Passkey {
  return {
    createdAt: passkey.created_at,
    id: passkey.id,
    label: passkey.label,
    lastUsedAt: passkey.last_used_at ?? null,
  };
}

export function toSessionUser(user: components["schemas"]["UserResponse"]): SessionUser {
  return { id: user.id, isGuest: user.is_guest };
}
