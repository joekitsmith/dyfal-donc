import type { NextConfig } from "next";

import { z } from "zod";

import { API_BASE_PATH } from "./src/config/paths";

const DEFAULT_API_URL = "http://localhost:8000";

/** Outside `next dev` the reverse proxy in front of the app sends `/api` to the API. */
const nextConfig: NextConfig = {
  output: "standalone",
  reactCompiler: true,
  rewrites() {
    if (process.env.NODE_ENV !== "development") {
      return [];
    }

    const apiUrl = z.url().parse(process.env.API_URL ?? DEFAULT_API_URL);

    return [{ destination: `${apiUrl}/:path*`, source: `${API_BASE_PATH}/:path*` }];
  },
  typedRoutes: true,
};

export default nextConfig;
