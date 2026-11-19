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
  await page.getByRole("radio", { name: "Slow only" }).check();
  await page.getByRole("button", { name: "Save" }).click();
  await expect(page.getByText("Saved", { exact: true })).toBeVisible();

  await page.getByRole("link", { name: "Back" }).click();
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
  await page.getByRole("radio", { name: "Standard only" }).check();
  await page.getByRole("button", { name: "Save" }).click();
  await expect(page.getByText("Saved", { exact: true })).toBeVisible();

  await page.reload();

  await expect(page.getByRole("radio", { name: "Standard only" })).toBeChecked();
});

test("the think time previews what it comes to, and Save says where the change has got to", async ({ page }) => {
  await startAsGuest(page);
  await page.goto("/settings");

  const save = page.getByRole("button", { name: /^(Save|Saving…|Saved)$/ });
  const slider = page.getByRole("slider", { name: "Think time" });

  await expect(page.getByRole("radio")).toHaveCount(3);
  await expect(save).toHaveText("Save");
  await expect(save).toHaveAttribute("aria-disabled", "true");

  await slider.focus();
  await page.keyboard.press("Home");
  await expect(page.getByText("0.5×", { exact: true }).first()).toBeVisible();
  await expect(page.getByText("A four-word sentence gets 2.5 seconds. Each block lasts 0.4 seconds.")).toBeVisible();

  for (let step = 0; step < 4; step += 1) {
    await page.keyboard.press("ArrowRight");
  }

  await expect(page.getByText("1.5×", { exact: true }).first()).toBeVisible();
  await expect(page.getByText("A four-word sentence gets 7.6 seconds. Each block lasts 1.1 seconds.")).toBeVisible();
  await expect(save).not.toHaveAttribute("aria-disabled", "true");

  await save.click();
  await expect(save).toHaveText("Saved");
  await expect(save).toHaveAttribute("aria-disabled", "true");

  await slider.focus();
  await page.keyboard.press("ArrowRight");
  await expect(save).toHaveText("Save");
  await expect(save).not.toHaveAttribute("aria-disabled", "true");
});

test("a change that could not be saved stays on the page, with a way to try again", async ({ page }) => {
  await startAsGuest(page);
  await page.goto("/settings");
  await page.route("**/api/me/settings", async (route) => {
    if (route.request().method() === "PATCH") {
      await route.fulfill({ body: "{}", status: 500 });
    } else {
      await route.continue();
    }
  });

  await page.getByRole("radio", { name: "Slow only" }).check();
  await page.getByRole("button", { name: "Save" }).click();

  await expect(page.getByText("Your changes couldn't be saved. They're still here, so try again.")).toBeVisible();
  await expect(page.getByRole("radio", { name: "Slow only" })).toBeChecked();
  await expect(page.getByRole("button", { name: "Save" })).not.toHaveAttribute("aria-disabled", "true");
});
