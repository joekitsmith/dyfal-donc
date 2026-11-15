import { expect, test } from "@playwright/test";

import { TEST_IDS } from "../src/config/test-ids";
import { instrumentAudio, requireStack, startAsGuest } from "./helpers";

test.beforeEach(async ({ page, request }) => {
  await requireStack(request);
  await instrumentAudio(page);
});

test("after a session the home screen recaps it and the summary lets a missed exercise be played again", async ({
  page,
}) => {
  await startAsGuest(page);
  await page.getByRole("button", { exact: true, name: "Start" }).click();
  await expect(page.getByTestId(TEST_IDS.welsh)).not.toHaveText("", { timeout: 30_000 });
  await page.keyboard.press("m");
  await page.waitForResponse((response) => response.url().endsWith("/outcomes"), { timeout: 30_000 });
  await expect(page.getByRole("timer")).toBeVisible();

  await page.getByRole("link", { name: "Home" }).click();

  const recap = page.getByRole("region", { name: "Latest session" });

  await expect(recap.getByRole("heading", { name: "This session so far" })).toBeVisible();
  await expect(recap).toContainText("1 exercise");
  await expect(recap.getByRole("region", { name: "New words" })).toBeVisible();
  await expect(page.getByRole("link", { name: "Continue learning" })).toBeVisible();

  await recap.getByRole("link", { name: "See details" }).click();
  await expect(page.getByRole("heading", { name: "Learning session" })).toBeVisible();

  const missed = page.getByRole("region", { name: "Missed exercises" });
  const clip = page.waitForResponse((response) => response.url().endsWith("/audio/welsh/standard"));

  await missed.getByRole("button", { name: /^Play (?!.*slowly)/ }).click();
  expect((await clip).status()).toBe(200);

  await page.getByRole("link", { name: "Keep going" }).click();
  await expect(page).toHaveURL(/\/learn$/);
});

test("a session that does not exist says so", async ({ page }) => {
  await startAsGuest(page);

  await page.goto("/learning-sessions/99");

  await expect(page.getByText("That learning session does not exist.")).toBeVisible();
});
