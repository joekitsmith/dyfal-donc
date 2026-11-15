import { expect, test } from "@playwright/test";

import { TEST_IDS } from "../src/config/test-ids";
import { instrumentAudio, requireStack, speedUpThinking, startAsGuest } from "./helpers";

test.beforeEach(async ({ page, request }) => {
  await requireStack(request);
  await speedUpThinking(page);
  await instrumentAudio(page);

  // A software passkey in the browser, so the real ceremonies run with nobody to approve them
  const session = await page.context().newCDPSession(page);

  await session.send("WebAuthn.enable");
  await session.send("WebAuthn.addVirtualAuthenticator", {
    options: {
      automaticPresenceSimulation: true,
      hasResidentKey: true,
      hasUserVerification: true,
      isUserVerified: true,
      protocol: "ctap2",
      transport: "internal",
    },
  });
});

test("a guest saves their progress with a passkey, signs out and signs back in", async ({ page }) => {
  await startAsGuest(page);
  await page.getByRole("button", { exact: true, name: "Start" }).click();
  await expect(page.getByTestId(TEST_IDS.welsh)).not.toHaveText("", { timeout: 30_000 });
  await page.keyboard.press("m");
  await page.waitForResponse((response) => response.url().endsWith("/outcomes"), { timeout: 30_000 });
  await expect(page.getByTestId(TEST_IDS.progress)).toContainText("Introduced: 1 of");

  await page.getByRole("link", { name: "Account" }).click();
  await expect(page.getByText("You are using a guest account.")).toBeVisible();
  await page.getByRole("button", { name: "Add a passkey" }).click();
  await expect(page.getByText("You are signed in with a passkey.")).toBeVisible();
  await expect(page.getByRole("list", { name: "Passkeys" }).getByRole("listitem")).toHaveCount(1);

  await page.getByRole("button", { name: "Sign out" }).click();
  await expect(page).toHaveURL(/\/welcome$/);

  await page.getByRole("button", { name: "Sign in with a passkey" }).click();
  await expect(page).toHaveURL(/\/learn$/);
  await expect(page.getByTestId(TEST_IDS.progress)).toContainText("Introduced: 1 of");
});
