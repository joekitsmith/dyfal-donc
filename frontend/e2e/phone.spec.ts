import { expect, test } from "@playwright/test";

import { instrumentAudio, requireStack, speedUpThinking } from "./helpers";

const MINIMUM_TOUCH_TARGET = 48;

test.beforeEach(async ({ page, request }) => {
  await requireStack(request);
  await speedUpThinking(page);
  await instrumentAudio(page);
});

test("the lesson fits a phone and its buttons are easy to tap", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("button", { exact: true, name: "Start" })).toBeVisible();
  await page.screenshot({ path: "test-results/phone-idle.png" });
  await page.getByRole("button", { exact: true, name: "Start" }).click();
  await expect(page.getByRole("heading", { level: 5 }).nth(0)).not.toHaveText("");
  await expect(page.getByRole("heading", { level: 5 }).nth(1)).not.toHaveText("", { timeout: 30_000 });
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
