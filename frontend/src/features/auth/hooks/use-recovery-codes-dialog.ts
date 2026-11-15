import { useState, useSyncExternalStore } from "react";

import { clearRecoveryCodes, getRecoveryCodes, subscribeToRecoveryCodes } from "../stores/recovery-codes-store";
import { downloadRecoveryCodes, recoveryCodesFileText } from "../utils/recovery-codes-file";

const NONE: readonly string[] = [];

/** The dialog that shows new recovery codes once, and only lets go of them when they are saved. */
export function useRecoveryCodesDialog() {
  const codes = useSyncExternalStore(subscribeToRecoveryCodes, getRecoveryCodes, () => NONE);
  const [saved, setSaved] = useState(false);
  const [copied, setCopied] = useState(false);

  return {
    codes,
    copy: {
      copied,
      onClick: () => {
        void navigator.clipboard.writeText(recoveryCodesFileText(codes)).then(() => {
          setCopied(true);
        });
      },
    },
    done: {
      disabled: !saved,
      onClick: () => {
        setSaved(false);
        setCopied(false);
        clearRecoveryCodes();
      },
    },
    download: () => {
      downloadRecoveryCodes(codes);
    },
    open: codes.length > 0,
    saved: {
      checked: saved,
      onChange: (checked: boolean) => {
        setSaved(checked);
      },
    },
  };
}
