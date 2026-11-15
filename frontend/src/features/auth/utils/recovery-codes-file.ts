import { RECOVERY_CODES_FILE_NAME } from "../constants";

/** The text of the file a person keeps their codes in. */
export function recoveryCodesFileText(codes: readonly string[]): string {
  return [
    "Dyfal donc recovery codes",
    "Each code works once, to get back into your account if you lose your passkey.",
    "",
    ...codes,
    "",
  ].join("\n");
}

/** Saves the codes as a text file, by way of a temporary link. */
export function downloadRecoveryCodes(codes: readonly string[]): void {
  const url = URL.createObjectURL(new Blob([recoveryCodesFileText(codes)], { type: "text/plain" }));
  const link = document.createElement("a");

  link.href = url;
  link.download = RECOVERY_CODES_FILE_NAME;
  link.click();
  URL.revokeObjectURL(url);
}
