import { z } from "zod";

import type { KeyValueStorage } from "@/utils/safe-storage";

import { LEARNER_STORAGE_KEY } from "../constants";

const learnerIdSchema = z.uuid();

export function readStoredLearnerId(storage: KeyValueStorage): null | string {
  const parsed = learnerIdSchema.safeParse(storage.getItem(LEARNER_STORAGE_KEY));

  return parsed.success ? parsed.data : null;
}

export function storeLearnerId(storage: KeyValueStorage, learnerId: string): void {
  storage.setItem(LEARNER_STORAGE_KEY, learnerId);
}
