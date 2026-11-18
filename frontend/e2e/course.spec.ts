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
  await expect(page.getByRole("button", { exact: true, name: `Play ${welsh}` })).toBeVisible();
  await expect(page.getByRole("region", { name: "Sentences you have got right" })).toBeVisible();
});

test("an item that has not been met is not found", async ({ page }) => {
  await startAsGuest(page);

  await page.goto("/course/items/lex%3Acig");

  await expect(page.getByText("We could not find that word.")).toBeVisible();
});
