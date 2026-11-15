import { useRecoveryCodeStatus } from "../api/use-recovery-code-status";
import { useReplaceRecoveryCodes } from "../api/use-replace-recovery-codes";
import { LOW_RECOVERY_CODES } from "../constants";

/** What the account screen shows about recovery codes, and the way to make new ones. */
export function useRecoveryCodesSection() {
  const status = useRecoveryCodeStatus();
  const replace = useReplaceRecoveryCodes();
  const remaining = status.data;

  return {
    failed: status.isError || replace.isError,
    generate: () => {
      replace.mutate();
    },
    isGenerating: replace.isPending,
    isLoading: remaining === undefined && !status.isError,
    low: remaining !== undefined && remaining <= LOW_RECOVERY_CODES,
    remaining,
  };
}
