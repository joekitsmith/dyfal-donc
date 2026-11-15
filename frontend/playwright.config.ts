import { defineConfig, devices } from "@playwright/test";

const WEB_URL = process.env.WEB_URL ?? "http://localhost:3000";

/** These tests need the stack running (`make stack-up`, then `poetry run poe db-create` the first time). */
export default defineConfig({
  projects: [
    { name: "desktop", testMatch: /lesson\.spec\.ts/, use: { ...devices["Desktop Chrome"] } },
    { name: "phone", testMatch: /phone\.spec\.ts/, use: { ...devices["Pixel 7"] } },
  ],
  reporter: "list",
  testDir: "e2e",
  timeout: 90_000,
  use: { baseURL: WEB_URL, trace: "retain-on-failure" },
  webServer: { command: "pnpm dev", reuseExistingServer: true, timeout: 120_000, url: WEB_URL },
  workers: 1,
});
