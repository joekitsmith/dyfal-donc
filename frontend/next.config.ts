import type { NextConfig } from "next";

import { z } from "zod";

import { API_BASE_PATH } from "./src/config/paths";

const DEFAULT_API_URL = "http://localhost:8000";

const apiUrl = z.url().parse(process.env.API_URL ?? DEFAULT_API_URL);

const nextConfig: NextConfig = {
  reactCompiler: true,
  rewrites() {
    return [{ destination: `${apiUrl}/:path*`, source: `${API_BASE_PATH}/:path*` }];
  },
  typedRoutes: true,
};

export default nextConfig;
