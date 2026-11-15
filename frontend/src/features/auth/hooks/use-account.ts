import { useDeleteAccount } from "../api/use-delete-account";
import { usePasskeys } from "../api/use-passkeys";
import { useRemovePasskey } from "../api/use-remove-passkey";
import { useSignOut } from "../api/use-sign-out";
import { useRequireSession } from "./use-require-session";

/** What the account screen shows and does. */
export function useAccount() {
  const { error: sessionError, user } = useRequireSession();
  const passkeys = usePasskeys();
  const removePasskey = useRemovePasskey();
  const signOut = useSignOut();
  const deleteAccount = useDeleteAccount();

  return {
    deleteAccount: deleteAccount.mutate,
    error: sessionError ?? passkeys.error ?? signOut.error ?? deleteAccount.error,
    isLoading: user === undefined || passkeys.isPending,
    passkeys: passkeys.data ?? [],
    removeFailed: removePasskey.isError,
    removePasskey: removePasskey.mutate,
    signOut: signOut.mutate,
    user,
  };
}
