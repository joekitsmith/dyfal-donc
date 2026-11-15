import { describe, expect, it } from "vitest";

import { isRetryable } from "@/features/lesson/utils/is-retryable";
import { withRetry } from "@/features/lesson/utils/with-retry";

describe("isRetryable", () => {
  it("retries the network failing and the server having a bad moment", () => {
    expect(isRetryable(new TypeError("Failed to fetch"))).toBe(true);
    expect(isRetryable({ status: 500 })).toBe(true);
    expect(isRetryable({ status: 502 })).toBe(true);
  });

  it("does not retry a refusal, or the speech service being down", () => {
    for (const status of [401, 404, 409, 410, 503]) {
      expect(isRetryable({ status })).toBe(false);
    }
  });
});

describe("withRetry", () => {
  it("runs again after a failure that may pass, and gives up after the delays", async () => {
    let calls = 0;
    const signal = new AbortController().signal;

    const result = await withRetry(
      () => {
        calls += 1;

        return calls < 3 ? Promise.reject(new TypeError("offline")) : Promise.resolve("done");
      },
      signal,
      [1, 1],
    );

    expect(result).toBe("done");
    await expect(withRetry(() => Promise.reject(new TypeError("offline")), signal, [1, 1])).rejects.toThrow("offline");
  });

  it("does not retry a refusal", async () => {
    let calls = 0;

    await expect(
      withRetry(
        () => {
          calls += 1;

          return Promise.reject(Object.assign(new Error("Gone"), { status: 410 }));
        },
        new AbortController().signal,
        [1, 1],
      ),
    ).rejects.toThrow("Gone");
    expect(calls).toBe(1);
  });
});
