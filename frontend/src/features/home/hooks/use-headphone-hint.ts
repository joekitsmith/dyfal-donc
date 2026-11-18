import { useSyncExternalStore } from "react";

import { getServerSnapshot, getSnapshot, isHintVisible, subscribe } from "../stores/headphone-hint-store";

export function useHeadphoneHint(): boolean {
  return isHintVisible(useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot));
}
