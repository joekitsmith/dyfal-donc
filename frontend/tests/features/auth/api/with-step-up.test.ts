import { describe, expect, it, vi } from "vitest";

import { ApiError } from "@/api/api-error";
import { withStepUp } from "@/features/auth/api/with-step-up";
import { cancelled, confirmed, pendingAction } from "@/features/auth/stores/step-up-store";
import { StepUpCancelledError } from "@/features/auth/utils/step-up";

const FORBIDDEN = 403;

async function untilAsked(): Promise<void> {
  await vi.waitFor(() => {
    expect(pendingAction()).not.toBeNull();
  });
}

describe("withStepUp", () => {
  it("makes the request once when nothing more is asked", async () => {
    const request = vi.fn().mockResolvedValue("done");

    expect(await withStepUp("new_codes", request)).toBe("done");
    expect(request).toHaveBeenCalledTimes(1);
  });

  it("asks for confirmation when the server wants a recent sign-in, then tries again", async () => {
    const request = vi.fn().mockRejectedValueOnce(new ApiError(FORBIDDEN)).mockResolvedValueOnce("done");

    const result = withStepUp("new_codes", request);

    await untilAsked();
    expect(request).toHaveBeenCalledTimes(1);
    confirmed();

    expect(await result).toBe("done");
    expect(request).toHaveBeenCalledTimes(2);
  });

  it("says which change is waiting to be confirmed", async () => {
    const request = vi.fn().mockRejectedValueOnce(new ApiError(FORBIDDEN)).mockResolvedValueOnce("done");

    const result = withStepUp("remove_passkey", request);

    await untilAsked();
    expect(pendingAction()).toBe("remove_passkey");
    confirmed();
    await result;

    expect(pendingAction()).toBeNull();
  });

  it("does not try again when the person gives up", async () => {
    const request = vi.fn().mockRejectedValue(new ApiError(FORBIDDEN));

    const result = withStepUp("new_codes", request);

    await untilAsked();
    cancelled();

    await expect(result).rejects.toThrow(StepUpCancelledError);
    expect(request).toHaveBeenCalledTimes(1);
  });

  it("does not ask about any other failure", async () => {
    const request = vi.fn().mockRejectedValue(new ApiError(500));

    await expect(withStepUp("new_codes", request)).rejects.toThrow(ApiError);
    expect(pendingAction()).toBeNull();
  });
});
