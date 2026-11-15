import type { Passkey } from "../types";

/** When a passkey was added and last used, in the reader's own date format. */
export function describePasskey(passkey: Passkey): string {
  const added = new Date(passkey.createdAt).toLocaleDateString();
  const used =
    passkey.lastUsedAt === null ? "never used" : `last used ${new Date(passkey.lastUsedAt).toLocaleDateString()}`;

  return `Added ${added}, ${used}`;
}
