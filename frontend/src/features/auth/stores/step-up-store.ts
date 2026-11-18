import { StepUpCancelledError } from "../utils/step-up";

/** What the change is that needs confirming, so the dialog can say so. */
export type StepUpAction = "add_passkey" | "delete_account" | "new_codes" | "remove_passkey";

type Waiting = { readonly action: StepUpAction; readonly settled: PromiseWithResolvers<undefined> };

let waiting: null | Waiting = null;
let switchedAccount = false;
let leaving: ReturnType<typeof setTimeout> | undefined;
const listeners = new Set<() => void>();

/** Asks the person to confirm with a passkey. It settles when they do, or when they give up. */
export function askToConfirm(action: StepUpAction): Promise<void> {
  if (waiting === null) {
    waiting = { action, settled: Promise.withResolvers<undefined>() };
    notify();
  }

  return waiting.settled.promise;
}

export function cancelled(): void {
  waiting?.settled.reject(new StepUpCancelledError());
  waiting = null;
  notify();
}

export function confirmed(): void {
  waiting?.settled.resolve(undefined);
  waiting = null;
  notify();
}

/** What is being confirmed, or null when nothing is. */
export function pendingAction(): null | StepUpAction {
  return waiting?.action ?? null;
}

/** Confirming with another account's passkey signs in to that account. The account screen says so, once. */
export function noteAccountSwitched(): void {
  switchedAccount = true;
  notify();
}

export function clearAccountSwitched(): void {
  switchedAccount = false;
  notify();
}

/**
 * The account screen is gone, and the notice goes with it, a moment later. A screen that is
 * shown again straight away, as in development, is the same visit and keeps it.
 */
export function leaveAccountScreen(): void {
  leaving = setTimeout(clearAccountSwitched, 0);
}

export function stayOnAccountScreen(): void {
  clearTimeout(leaving);
}

export function hasSwitchedAccount(): boolean {
  return switchedAccount;
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
