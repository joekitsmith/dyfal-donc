import { StepUpCancelledError } from "../utils/step-up";

type Waiting = PromiseWithResolvers<undefined>;

let waiting: null | Waiting = null;
const listeners = new Set<() => void>();

/** Asks the person to confirm with a passkey. It settles when they do, or when they give up. */
export function askToConfirm(): Promise<void> {
  if (waiting === null) {
    waiting = Promise.withResolvers<undefined>();
    notify();
  }

  return waiting.promise;
}

export function confirmed(): void {
  waiting?.resolve(undefined);
  waiting = null;
  notify();
}

export function cancelled(): void {
  waiting?.reject(new StepUpCancelledError());
  waiting = null;
  notify();
}

export function isAwaitingConfirmation(): boolean {
  return waiting !== null;
}

export function subscribeToConfirmation(listener: () => void): () => void {
  listeners.add(listener);

  return () => {
    listeners.delete(listener);
  };
}

function notify(): void {
  for (const listener of listeners) {
    listener();
  }
}
