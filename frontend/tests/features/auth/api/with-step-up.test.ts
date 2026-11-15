import { describe, expect, it, vi } from "vitest";

import { ApiError } from "@/api/api-error";
import { withStepUp } from "@/features/auth/api/with-step-up";
import { cancelled, confirmed, isAwaitingConfirmation } from "@/features/auth/stores/step-up-store";
import { StepUpCancelledError } from "@/features/auth/utils/step-up";

const FORBIDDEN = 403;

async function untilAsked(): Promise<void> {
  await vi.waitFor(() => {
    expect(isAwaitingConfirmation()).toBe(true);
  });
}

describe("withStepUp", () => {
  it("makes the request once when nothing more is asked", async () => {
    const request = vi.fn().mockResolvedValue("done");

    expect(await withStepUp(request)).toBe("done");
    expect(request).toHaveBeenCalledTimes(1);
  });

  it("asks for confirmation when the server wants a recent sign-in, then tries again", async () => {
    const request = vi.fn().mockRejectedValueOnce(new ApiError(FORBIDDEN)).mockResolvedValueOnce("done");

    const result = withStepUp(request);

    await untilAsked();
    expect(request).toHaveBeenCalledTimes(1);
    confirmed();

    expect(await result).toBe("done");
    expect(request).toHaveBeenCalledTimes(2);
  });

  it("does not try again when the person gives up", async () => {
    const request = vi.fn().mockRejectedValue(new ApiError(FORBIDDEN));

    const result = withStepUp(request);

    await untilAsked();
    cancelled();

    await expect(result).rejects.toThrow(StepUpCancelledError);
    expect(request).toHaveBeenCalledTimes(1);
  });

  it("does not ask about any other failure", async () => {
    const request = vi.fn().mockRejectedValue(new ApiError(500));

    await expect(withStepUp(request)).rejects.toThrow(ApiError);
    expect(isAwaitingConfirmation()).toBe(false);
  });
});
