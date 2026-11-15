import type { PasskeyFailure } from "../types";

import { useRegisterPasskey } from "../api/use-register-passkey";
import { passkeyFailure } from "../utils/passkey-failure";

/** Adds a passkey to the signed-in account, which is what keeps a guest's progress. */
export function useSaveProgress(onSaved?: () => void) {
  const register = useRegisterPasskey();
  const failure: null | PasskeyFailure = register.isError ? passkeyFailure(register.error) : null;

  return {
    failure,
    isSaving: register.isPending,
    save: (label?: string) => {
      register.mutate(label, {
        onSuccess: () => {
          onSaved?.();
        },
      });
    },
  };
}
