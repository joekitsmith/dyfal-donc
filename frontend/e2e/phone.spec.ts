import { expect, test } from "@playwright/test";

import { TEST_IDS } from "../src/config/test-ids";
import { requireStack, startAsGuest, startButton, startLesson } from "./helpers";
import { smallTargets } from "./inspect";

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
  // A touch screen has no keys to press, whatever its width
  await expect(page.getByText("Space", { exact: true })).toBeHidden();
  await startLesson(page);
  await expect(page.getByTestId(TEST_IDS.english)).not.toHaveText("");
  await expect(page.getByTestId(TEST_IDS.welsh)).not.toHaveText("", { timeout: 30_000 });
  await page.screenshot({ path: "test-results/phone-exercise.png" });
  await expect(page.getByText("M", { exact: true })).toBeHidden();

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

  // The screens that came with the redesign, on a phone: nothing that is pressed is under 48 px, and each is kept as a picture
  for (const [path, name] of [
    ["/", "home"],
    ["/account", "account"],
    ["/settings", "settings"],
    ["/course", "course"],
  ] as const) {
    await page.goto(path);
    await expect(page.getByRole("button", { name: "Menu" }).or(page.getByRole("link", { name: "Back" }))).toBeVisible();
    await page.screenshot({ fullPage: true, path: `test-results/phone-${name}.png` });
    expect(await smallTargets(page), `${name}: targets under 48 px`).toEqual([]);
  }
});
