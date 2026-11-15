import type { ApiClient } from "@/api/client";

const UNAUTHORIZED = 401;

/** Starts straight away as a guest, so there is no sign-up in the way. */
async function startGuest(client: ApiClient): Promise<string> {
  const { data, response } = await client.POST("/auth/guest");

  if (data === undefined) {
    throw new Error(`Could not start (status ${response.status})`);
  }

  return data.id;
}

/** Whoever the session cookie says is signed in, otherwise a new guest. */
export async function resolveLearner(client: ApiClient): Promise<string> {
  const { data, response } = await client.GET("/me");

  if (data !== undefined) {
    return data.id;
  }

  if (response.status === UNAUTHORIZED) {
    return startGuest(client);
  }

  throw new Error(`Could not check who is signed in (status ${response.status})`);
}

/** Deletes the account and everything in it, then starts again as a new guest. */
export async function startOver(client: ApiClient): Promise<string> {
  const { response } = await client.DELETE("/me");

  if (!response.ok && response.status !== UNAUTHORIZED) {
    throw new Error(`Could not start over (status ${response.status})`);
  }

  return startGuest(client);
}
