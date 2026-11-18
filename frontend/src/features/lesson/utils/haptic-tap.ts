const TAP_MILLISECONDS = 10;

/** A short buzz for a press on the screen, where the device can. */
export function hapticTap(): void {
  if ("vibrate" in navigator) {
    navigator.vibrate(TAP_MILLISECONDS);
  }
}
