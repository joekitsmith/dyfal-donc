import type { ApiClient } from "@/api/client";
import type { KeyValueStorage } from "@/utils/safe-storage";

import { readStoredLearnerId, storeLearnerId } from "./learner-storage";

const NOT_FOUND = 404;

export async function createLearner(client: ApiClient, storage: KeyValueStorage): Promise<string> {
  const { data, response } = await client.POST("/learners");

  if (data === undefined) {
    throw new Error(`Could not create a learner (status ${response.status})`);
  }

  storeLearnerId(storage, data.id);

  return data.id;
}

/**
 * The stored learner if the server still knows it, otherwise a new one. The database is wiped
 * when the course changes, so a stored id can outlive its learner.
 */
export async function resolveLearner(client: ApiClient, storage: KeyValueStorage): Promise<string> {
  const storedId = readStoredLearnerId(storage);

  if (storedId === null) {
    return createLearner(client, storage);
  }

  const { response } = await client.GET("/learners/{learner_id}/progress", {
    params: { path: { learner_id: storedId } },
  });

  if (response.ok) {
    return storedId;
  }

  if (response.status === NOT_FOUND) {
    return createLearner(client, storage);
  }

  throw new Error(`Could not check the learner (status ${response.status})`);
}
