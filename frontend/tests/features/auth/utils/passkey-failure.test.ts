import { WebAuthnError } from "@simplewebauthn/browser";
import { describe, expect, it } from "vitest";

import { ApiError } from "@/api/api-error";
import { passkeyFailure } from "@/features/auth/utils/passkey-failure";

function webAuthnError(code: ConstructorParameters<typeof WebAuthnError>[0]["code"], causeName: string) {
  const cause = new Error("The browser said no");

  cause.name = causeName;

  return new WebAuthnError({ cause, code, message: "Failed" });
}

describe("passkeyFailure", () => {
  it("treats a dismissed prompt as cancelled", () => {
    expect(passkeyFailure(webAuthnError("ERROR_PASSTHROUGH_SEE_CAUSE_PROPERTY", "NotAllowedError"))).toBe("cancelled");
    expect(passkeyFailure(webAuthnError("ERROR_CEREMONY_ABORTED", "AbortError"))).toBe("cancelled");
  });

  it("knows a passkey that is already saved", () => {
    expect(passkeyFailure(webAuthnError("ERROR_AUTHENTICATOR_PREVIOUSLY_REGISTERED", "InvalidStateError"))).toBe(
      "already_registered",
    );
    expect(passkeyFailure(new ApiError(409))).toBe("already_registered");
  });

  it("knows a passkey the server did not recognise", () => {
    expect(passkeyFailure(new ApiError(400))).toBe("not_recognised");
  });

  it("calls anything else something that went wrong", () => {
    expect(passkeyFailure(new ApiError(500))).toBe("other");
    expect(passkeyFailure(new Error("Network down"))).toBe("other");
    expect(passkeyFailure(webAuthnError("ERROR_INVALID_RP_ID", "SecurityError"))).toBe("other");
  });
});
