import { expect, test } from "@playwright/test";

import { TEST_IDS } from "../src/config/test-ids";
import { chooseFromMenu, requireStack, startAsGuest, startLesson } from "./helpers";

test.beforeEach(async ({ request }) => {
  await requireStack(request);
});

test("the course lists what was met, can be searched, and opens a word with the sentences it was in", async ({
  page,
}) => {
  await startAsGuest(page);
  await startLesson(page);
  await expect(page.getByTestId(TEST_IDS.welsh)).not.toHaveText("", { timeout: 30_000 });
  await page.waitForResponse((response) => response.url().endsWith("/outcomes"), { timeout: 30_000 });

  await chooseFromMenu(page, "button", "Stop for now");
  await chooseFromMenu(page, "link", "Look something up");

  await expect(page.getByRole("heading", { level: 1, name: "Everything you've met" })).toBeVisible();
  await expect(page.getByRole("region", { name: "Later in the course" })).toBeVisible();
  await expect(
    page.getByRole("region", { name: "Things you can say" }).getByRole("button", { name: / slowly$/ }),
  ).toBeVisible();

  await expect(page.getByRole("heading", { level: 2 }).first()).toHaveText("Everyday talk");
  await expect(page.getByText("You're here")).toBeVisible();

  const word = page.getByRole("region", { name: "Words" }).getByRole("link").first();
  const welsh = (await word.locator("[lang=cy]").textContent()) ?? "";

  await page.getByRole("searchbox", { name: "Search in English or Welsh" }).fill(welsh);
  await page.getByRole("region", { name: "Search results" }).getByRole("link").first().click();

  await expect(page).toHaveURL(/\/course\/items\/.+/);
  await expect(page.getByRole("heading", { level: 1, name: welsh })).toBeVisible();

  const clip = page.waitForResponse((response) => /\/items\/.+\/audio$/.test(response.url()));

  await page.getByRole("button", { name: "Hear it" }).click();
  expect((await clip).status()).toBe(200);
  await expect(page.getByRole("region", { name: "Sentences you've said with it" })).toBeVisible();
});

test("an item that has not been met is not found", async ({ page }) => {
  await startAsGuest(page);

  await page.goto("/course/items/lex%3Acig");

  await expect(page.getByText("We couldn't find that.")).toBeVisible();
});

test("from a running lesson the course opens over it, a word opens inside it, and the lesson is still paused on its sentence", async ({
  page,
}) => {
  await startAsGuest(page);
  await startLesson(page);

  const english = page.getByTestId(TEST_IDS.english);

  await expect(english).not.toHaveText("");

  const first = (await english.textContent()) ?? "";

  await expect(page.getByTestId(TEST_IDS.welsh)).not.toHaveText("", { timeout: 30_000 });
  await page.keyboard.press("m");
  await page.waitForResponse((response) => response.url().endsWith("/outcomes"), { timeout: 30_000 });
  await expect(english).not.toHaveText(first, { timeout: 30_000 });

  const current = (await english.textContent()) ?? "";

  await chooseFromMenu(page, "button", "Look something up");

  const sheet = page.getByRole("dialog", { name: "Everything you've met" });

  await expect(sheet.getByRole("heading", { level: 1, name: "Everything you've met" })).toBeVisible();
  await expect(page).toHaveURL(/\/$/);
  // The lesson pauses as soon as it can, which is once the next sentence's audio has started
  await expect(page.getByRole("button", { includeHidden: true, name: /^Resume/ })).toBeVisible();

  await sheet.getByRole("region", { name: "Words" }).getByRole("link").first().click();
  await expect(sheet.getByRole("heading", { level: 1 })).not.toHaveText("Everything you've met");
  await expect(page).toHaveURL(/\/$/);
  await expect(sheet.getByRole("button", { name: "Hear it" })).toBeVisible();

  await sheet.getByRole("button", { name: "Everything you've met" }).click();
  await expect(sheet.getByRole("heading", { level: 1, name: "Everything you've met" })).toBeVisible();

  await sheet.getByRole("button", { name: "Back" }).click();
  await expect(sheet).toBeHidden();

  await expect(english).toHaveText(current);
  await expect(page.getByRole("button", { name: /^Resume/ })).toBeVisible();
});
