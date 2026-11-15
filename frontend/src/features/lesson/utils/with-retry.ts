import { RETRY_DELAYS_MILLISECONDS } from "../constants";
import { isRetryable } from "./is-retryable";

/** Runs the request again after each delay while it fails in a way that may pass. Aborting stops the waiting. */
export async function withRetry<Result>(
  run: () => Promise<Result>,
  signal: AbortSignal,
  delays: readonly number[] = RETRY_DELAYS_MILLISECONDS,
): Promise<Result> {
  for (const delay of delays) {
    try {
      return await run();
    } catch (error) {
      if (signal.aborted || !isRetryable(error)) {
        throw error;
      }

      await wait(delay, signal);
    }
  }

  return run();
}

function wait(milliseconds: number, signal: AbortSignal): Promise<void> {
  return new Promise((resolve) => {
    const handle = setTimeout(resolve, milliseconds);

    signal.addEventListener(
      "abort",
      () => {
        clearTimeout(handle);
        resolve();
      },
      { once: true },
    );
  });
}
