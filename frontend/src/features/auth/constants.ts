export const SESSION_QUERY_KEY = ["session"] as const;
export const PASSKEYS_QUERY_KEY = ["passkeys"] as const;
export const RECOVERY_STATUS_QUERY_KEY = ["recovery-codes"] as const;

/** At or below this many unused codes the account screen warns. */
export const LOW_RECOVERY_CODES = 3;

export const BAD_REQUEST_STATUS = 400;
export const UNAUTHORIZED_STATUS = 401;
export const CONFLICT_STATUS = 409;

export const MAXIMUM_LABEL_LENGTH = 128;
export const MAXIMUM_CODE_LENGTH = 64;

export const RECOVERY_CODES_FILE_NAME = "dyfal-donc-recovery-codes.txt";
export const RECOVERY_CODE_NOT_RECOGNISED_MESSAGE = "That code was not recognised, or it has already been used.";
export const RECOVERY_CODE_FAILED_MESSAGE = "Something went wrong. Try again.";

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
