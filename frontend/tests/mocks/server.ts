import { setupServer } from "msw/node";
import { createOpenApiHttp } from "openapi-msw";

import type { paths } from "@/api/schema";

export const API_URL = "http://api.test";

export const apiHttp = createOpenApiHttp<paths>({ baseUrl: API_URL });

export const server = setupServer();
