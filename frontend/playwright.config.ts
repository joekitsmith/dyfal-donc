import { defineConfig, devices } from "@playwright/test";

const DEV_SERVER_URL = "http://localhost:3000";
const WEB_URL = process.env.WEB_URL ?? DEV_SERVER_URL;

/**
 * These tests need the stack running (`make stack-up`). With `WEB_URL` set they drive that address,
 * as `make web-e2e` does; without it they start `pnpm dev`, which needs `make stack-up-debug`.
 */
export default defineConfig({
  projects: [
    {
      name: "desktop",
      testMatch: /(lesson|passkey|settings|summary)\.spec\.ts/,
      use: { ...devices["Desktop Chrome"] },
    },
    { name: "phone", testMatch: /phone\.spec\.ts/, use: { ...devices["Pixel 7"] } },
  ],
  reporter: "list",
  testDir: "e2e",
  timeout: 90_000,
  use: { baseURL: WEB_URL, trace: "retain-on-failure" },
  webServer:
    process.env.WEB_URL === undefined
      ? { command: "pnpm dev", reuseExistingServer: true, timeout: 120_000, url: DEV_SERVER_URL }
      : [],
  workers: 1,
});
