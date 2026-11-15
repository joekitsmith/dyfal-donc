export type Passkey = {
  readonly createdAt: string;
  readonly id: string;
  readonly label: string;
  readonly lastUsedAt: null | string;
};

export type PasskeyFailure = "already_registered" | "cancelled" | "not_recognised" | "other" | "unsupported";

export type SessionUser = {
  readonly id: string;
  readonly isGuest: boolean;
};
