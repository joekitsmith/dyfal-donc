export const SESSION_QUERY_KEY = ["session"] as const;
export const PASSKEYS_QUERY_KEY = ["passkeys"] as const;

export const BAD_REQUEST_STATUS = 400;
export const UNAUTHORIZED_STATUS = 401;
export const CONFLICT_STATUS = 409;

export const MAXIMUM_LABEL_LENGTH = 128;

export const FAILURE_MESSAGES = {
  already_registered: "This passkey is already saved to your account.",
  cancelled: "Cancelled, so nothing was changed.",
  not_recognised: "That passkey was not recognised. Try another, or start as a guest.",
  other: "Something went wrong. Try again.",
  unsupported: "This browser cannot use passkeys.",
} as const;
