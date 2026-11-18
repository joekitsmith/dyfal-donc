import { useDeleteAccount } from "../api/use-delete-account";
import { usePasskeys } from "../api/use-passkeys";
import { useRemovePasskey } from "../api/use-remove-passkey";
import { useSignOut } from "../api/use-sign-out";
import { ACCOUNT_FAILURES } from "../constants";
import { useRecoveryCodesSection } from "./use-recovery-codes-section";
import { useRequireSession } from "./use-require-session";

/** What the account screen shows and does. */
export function useAccount() {
  const { error: sessionError, user } = useRequireSession();
  const passkeys = usePasskeys();
  const removePasskey = useRemovePasskey();
  const signOut = useSignOut();
  const deleteAccount = useDeleteAccount();
  const recovery = useRecoveryCodesSection(user !== undefined && !user.isGuest);

  return {
    deleteAccount: () => {
      deleteAccount.mutate();
    },
    /** The screen could not load, as opposed to a change that did not happen. */
    error: sessionError ?? passkeys.error,
    /** What did not happen, if something did not. */
    failure: failureOf({
      deleteAccount: deleteAccount.isError,
      recovery: recovery.failed,
      removePasskey: removePasskey.isError,
      signOut: signOut.isError,
    }),
    isLoading: user === undefined || passkeys.isPending,
    passkeys: {
      items: passkeys.data ?? [],
      remove: (passkeyId: string) => {
        removePasskey.mutate(passkeyId);
      },
    },
    recovery,
    retry: () => {
      void passkeys.refetch();
    },
    signOut: () => {
      signOut.mutate();
    },
    user,
  };
}

function failureOf(failed: {
  readonly deleteAccount: boolean;
  readonly recovery: boolean;
  readonly removePasskey: boolean;
  readonly signOut: boolean;
}): null | string {
  if (failed.removePasskey) {
    return ACCOUNT_FAILURES.removePasskey;
  }

  if (failed.recovery) {
    return ACCOUNT_FAILURES.codes;
  }

  if (failed.signOut) {
    return ACCOUNT_FAILURES.signOut;
  }

  return failed.deleteAccount ? ACCOUNT_FAILURES.deleteAccount : null;
}
