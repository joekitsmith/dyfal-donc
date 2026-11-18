export const SESSION_QUERY_KEY = ["session"] as const;
export const PASSKEYS_QUERY_KEY = ["passkeys"] as const;
export const RECOVERY_STATUS_QUERY_KEY = ["recovery-codes"] as const;

/** At or below this many unused codes the account screen warns. */
export const LOW_RECOVERY_CODES = 3;

/** How many codes a set has. The server reports only how many are unused. */
export const RECOVERY_CODE_TOTAL = 10;

/** The name the server gives a passkey that was not named. */
export const DEFAULT_PASSKEY_LABEL = "Passkey";

/** What the account screen says when a change did not happen. */
export const ACCOUNT_FAILURES = {
  codes: "Something went wrong. Try again.",
  deleteAccount: "Your account wasn't deleted. Try again.",
  removePasskey: "The passkey could not be removed. Try again.",
  signOut: "You weren't signed out. Try again.",
} as const;

export const BAD_REQUEST_STATUS = 400;
export const UNAUTHORIZED_STATUS = 401;
export const CONFLICT_STATUS = 409;

export const MAXIMUM_LABEL_LENGTH = 128;
export const MAXIMUM_CODE_LENGTH = 64;

export const RECOVERY_CODES_FILE_NAME = "dyfal-donc-recovery-codes.txt";
export const RECOVERY_CODE_EMPTY_MESSAGE = "Enter a recovery code.";
export const RECOVERY_CODE_NOT_RECOGNISED_MESSAGE = "That code didn't work. It may be mistyped or already used.";
export const RECOVERY_CODE_FAILED_MESSAGE = "Something went wrong on our side. Try again in a moment.";

export const FAILURE_MESSAGES = {
  already_registered: "This passkey is already saved to your account.",
  cancelled: "Cancelled, so nothing was changed.",
  not_recognised: "That passkey was not recognised. Try another, or start as a guest.",
  other: "Something went wrong. Try again.",
  unsupported: "This browser cannot use passkeys.",
} as const;

export const WELCOME_NOTICES = {
  cancelled: "Nothing changed. You can try again whenever you like.",
  not_recognised: "We don't recognise that passkey. Try another, or start as a guest.",
  other: "Something went wrong on our side. Try again in a moment.",
  unsupported: "This browser can't use passkeys, so signing in isn't available here. You can still start as a guest.",
} as const;
