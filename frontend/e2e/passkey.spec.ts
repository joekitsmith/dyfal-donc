import { expect, test } from "@playwright/test";

import { TEST_IDS } from "../src/config/test-ids";
import { installPasskeyDevice, openLesson, requireStack, saveProgressAndKeepFirstCode, startAsGuest } from "./helpers";

let device: Awaited<ReturnType<typeof installPasskeyDevice>>;

test.beforeEach(async ({ page, request }) => {
  await requireStack(request);
  device = await installPasskeyDevice(page);
});

test("a guest saves their progress with a passkey, signs out and signs back in", async ({ page }) => {
  await startAsGuest(page);
  await page.getByRole("button", { exact: true, name: "Start" }).click();
  await expect(page.getByTestId(TEST_IDS.welsh)).not.toHaveText("", { timeout: 30_000 });
  await page.keyboard.press("m");
  await page.waitForResponse((response) => response.url().endsWith("/outcomes"), { timeout: 30_000 });
  await expect(page.getByTestId(TEST_IDS.progress)).toContainText("Introduced: 1 of");

  await saveProgressAndKeepFirstCode(page);
  await expect(page.getByRole("list", { name: "Passkeys" }).getByRole("listitem")).toHaveCount(1);

  await page.getByRole("button", { name: "Sign out" }).click();
  await expect(page).toHaveURL(/\/welcome$/);

  await page.getByRole("button", { name: "Sign in with a passkey" }).click();
  await expect(page).toHaveURL(/\/$/);
  await openLesson(page);
  await expect(page.getByTestId(TEST_IDS.progress)).toContainText("Introduced: 1 of");
});

test("a recovery code gets someone back in once, after they lose their passkey", async ({ page }) => {
  await startAsGuest(page);

  const code = await saveProgressAndKeepFirstCode(page);

  await page.getByRole("button", { name: "Sign out" }).click();
  await expect(page).toHaveURL(/\/welcome$/);
  await device.replace();

  await page.getByRole("link", { name: "Use a recovery code" }).click();
  await page.getByLabel("Recovery code").fill(code.toLowerCase());
  await page.getByRole("button", { name: "Sign in" }).click();
  await expect(page.getByText("You're signed in")).toBeVisible();

  await page.getByRole("button", { name: "Add a passkey" }).click();
  await page.getByRole("link", { name: "Carry on without one" }).click();
  await expect(page).toHaveURL(/\/$/);
  await page.getByRole("link", { name: "Account" }).click();
  await expect(page.getByRole("list", { name: "Passkeys" }).getByRole("listitem")).toHaveCount(2);
  await expect(page.getByText("9 unused.")).toBeVisible();

  await page.getByRole("button", { name: "Sign out" }).click();
  await page.getByRole("link", { name: "Use a recovery code" }).click();
  await page.getByLabel("Recovery code").fill(code);
  await page.getByRole("button", { name: "Sign in" }).click();
  await expect(page.getByText("That code didn't work. It may be mistyped or already used.")).toBeVisible();
});
