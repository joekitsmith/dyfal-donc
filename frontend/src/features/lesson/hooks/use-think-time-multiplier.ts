import { useState } from "react";
import { z } from "zod";

import { browserStorage } from "@/utils/safe-storage";

import {
  THINK_MULTIPLIER_DEFAULT,
  THINK_MULTIPLIER_MAXIMUM,
  THINK_MULTIPLIER_MINIMUM,
  THINK_MULTIPLIER_STORAGE_KEY,
} from "../constants";

const multiplierSchema = z.coerce.number().min(THINK_MULTIPLIER_MINIMUM).max(THINK_MULTIPLIER_MAXIMUM);

/** The learner's think-time setting, kept in localStorage. Only rendered after hydration, so it can read it at once. */
export function useThinkTimeMultiplier() {
  const [multiplier, setMultiplier] = useState(() => {
    const stored = browserStorage.getItem(THINK_MULTIPLIER_STORAGE_KEY);
    const parsed = stored === null ? undefined : multiplierSchema.safeParse(stored);

    return parsed?.success === true ? parsed.data : THINK_MULTIPLIER_DEFAULT;
  });

  return [
    multiplier,
    (next: number) => {
      setMultiplier(next);
      browserStorage.setItem(THINK_MULTIPLIER_STORAGE_KEY, String(next));
    },
  ] as const;
}
