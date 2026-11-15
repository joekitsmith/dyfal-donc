import createFetchClient from "openapi-fetch";
import createQueryApi from "openapi-react-query";

import { API_BASE_PATH } from "@/config/paths";

import type { paths } from "./schema";

export type ApiClient = ReturnType<typeof createApiClient>;

export function createApiClient(baseUrl: string = API_BASE_PATH) {
  return createFetchClient<paths>({ baseUrl });
}

export const apiClient = createApiClient();

export const queryApi = createQueryApi(apiClient);
