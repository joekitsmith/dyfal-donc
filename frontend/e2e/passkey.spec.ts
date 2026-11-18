import { expect, test } from "@playwright/test";

import { TEST_IDS } from "../src/config/test-ids";
import {
  chooseFromMenu,
  installPasskeyDevice,
  requireStack,
  saveProgressAndKeepFirstCode,
  startAsGuest,
  startLesson,
} from "./helpers";

let device: Awaited<ReturnType<typeof installPasskeyDevice>>;

test.beforeEach(async ({ page, request }) => {
  await requireStack(request);
  device = await installPasskeyDevice(page);
});

test("a guest saves their progress with a passkey, signs out and signs back in", async ({ page }) => {
  await startAsGuest(page);
  await startLesson(page);
  await expect(page.getByTestId(TEST_IDS.welsh)).not.toHaveText("", { timeout: 30_000 });
  await page.keyboard.press("m");
  await page.waitForResponse((response) => response.url().endsWith("/outcomes"), { timeout: 30_000 });

  await saveProgressAndKeepFirstCode(page);
  await expect(page.getByRole("list", { name: "Passkeys" }).getByRole("listitem")).toHaveCount(1);

  await page.getByRole("button", { name: "Sign out" }).click();
  await expect(page).toHaveURL(/\/welcome$/);

  await page.getByRole("button", { name: "Sign in with a passkey" }).click();
  await expect(page).toHaveURL(/\/$/);
  await expect(page.getByRole("region", { name: "Latest session" })).toContainText("1 sentence");
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
  await chooseFromMenu(page, "link", "Account");
  await expect(page.getByRole("list", { name: "Passkeys" }).getByRole("listitem")).toHaveCount(2);
  await expect(page.getByText("9 unused.")).toBeVisible();

  await page.getByRole("button", { name: "Sign out" }).click();
  await page.getByRole("link", { name: "Use a recovery code" }).click();
  await page.getByLabel("Recovery code").fill(code);
  await page.getByRole("button", { name: "Sign in" }).click();
  await expect(page.getByText("That code didn't work. It may be mistyped or already used.")).toBeVisible();
});

test("a passkey added from the lesson shows a confirmation that stays until the next exercise", async ({ page }) => {
  await startAsGuest(page);
  // Reaching five introduced items takes about ten exercises, so the lesson is told they are met
  await page.route("**/api/me/progress", async (route) => {
    const response = await route.fetch();

    const progress = (await response.json()) as Record<string, unknown>;

    await route.fulfill({ json: { ...progress, introduced: 5 }, response });
  });
  await startLesson(page);
  await expect(page.getByTestId(TEST_IDS.english)).not.toHaveText("");

  const prompt = page.getByText("Your progress is saved on this browser.");

  await expect(prompt).toBeVisible();
  await page.getByRole("button", { name: "Add a passkey" }).click();

  const dialog = page.getByRole("dialog", { name: "Save your recovery codes" });

  await dialog.getByLabel("I have saved these codes").check();
  await dialog.getByRole("button", { name: "Done" }).click();

  const confirmation = page.getByText("Passkey added. You can sign in from any device now.");

  await expect(confirmation).toBeVisible();
  await expect(prompt).toBeHidden();
  await expect(page.getByTestId(TEST_IDS.english)).not.toHaveText("");

  // It goes when the next exercise begins
  const first = await page.getByTestId(TEST_IDS.english).textContent();

  await expect(page.getByTestId(TEST_IDS.english)).not.toHaveText(first ?? "", { timeout: 45_000 });
  await expect(confirmation).toBeHidden();
});
