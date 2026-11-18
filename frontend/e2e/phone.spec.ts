import { expect, test } from "@playwright/test";

import { TEST_IDS } from "../src/config/test-ids";
import { requireStack, startAsGuest, startButton, startLesson } from "./helpers";

const MINIMUM_TOUCH_TARGET = 48;

test.beforeEach(async ({ request }) => {
  await requireStack(request);
});

test("the lesson fits a phone and its buttons are easy to tap", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("button", { name: "Try it now" })).toBeVisible();
  await page.screenshot({ path: "test-results/phone-welcome.png" });
  await startAsGuest(page);
  await expect(startButton(page)).toBeVisible();
  await page.screenshot({ path: "test-results/phone-idle.png" });
  await startLesson(page);
  await expect(page.getByTestId(TEST_IDS.english)).not.toHaveText("");
  await expect(page.getByTestId(TEST_IDS.welsh)).not.toHaveText("", { timeout: 30_000 });
  await page.screenshot({ path: "test-results/phone-exercise.png" });

  const fits = await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth);

  expect(fits).toBe(true);

  for (const button of await page.getByRole("button").all()) {
    const label = (await button.getAttribute("aria-label")) ?? (await button.textContent()) ?? "";

    // The devtools toggles only exist in development
    if (/dev ?tools/i.test(label)) {
      continue;
    }

    expect((await button.boundingBox())?.height, label).toBeGreaterThanOrEqual(MINIMUM_TOUCH_TARGET);
  }
});
