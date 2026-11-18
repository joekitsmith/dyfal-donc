import { expect, test } from "@playwright/test";

import { TEST_IDS } from "../src/config/test-ids";
import { chooseFromMenu, requireStack, startAsGuest, startLesson } from "./helpers";

const AUDIO_PATH = /\/api\/exercises\/.+\/audio\/(?<track>.+)$/;

test.beforeEach(async ({ request }) => {
  await requireStack(request);
});

test("with slow Welsh only the lesson never fetches the standard Welsh", async ({ page }) => {
  const tracks: (string | undefined)[] = [];

  page.on("request", (request) => {
    tracks.push(AUDIO_PATH.exec(request.url())?.groups?.track);
  });

  await startAsGuest(page);
  await chooseFromMenu(page, "link", "Settings");
  await page.getByLabel("Welsh audio").click();
  await page.getByRole("option", { name: "Slow only" }).click();
  await page.getByRole("button", { name: "Save" }).click();
  await expect(page.getByText("Saved", { exact: true })).toBeVisible();

  await page.getByRole("link", { name: "Back to the lesson" }).click();
  await startLesson(page);
  await expect(page.getByTestId(TEST_IDS.welsh)).not.toHaveText("", { timeout: 30_000 });
  await page.keyboard.press("m");
  await page.waitForResponse((response) => response.url().endsWith("/outcomes"), { timeout: 30_000 });

  expect(tracks).toContain("welsh/slow");
  expect(tracks).not.toContain("welsh/standard");
});

test("the settings are still there after a reload", async ({ page }) => {
  await startAsGuest(page);
  await page.goto("/settings");
  await page.getByLabel("Welsh audio").click();
  await page.getByRole("option", { name: "Standard only" }).click();
  await page.getByRole("button", { name: "Save" }).click();
  await expect(page.getByText("Saved", { exact: true })).toBeVisible();

  await page.reload();

  await expect(page.getByLabel("Welsh audio")).toHaveText("Standard only");
});
