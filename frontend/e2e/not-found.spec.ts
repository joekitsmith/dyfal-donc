import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

const UNKNOWN_ADDRESS = "/no-such-page";
const WCAG_AA_TAGS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"];

test("an unknown address says so and leads back to the start", async ({ page }) => {
  const response = await page.goto(UNKNOWN_ADDRESS);

  expect(response?.status()).toBe(404);
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("This page isn't here");

  await page.getByRole("link", { name: "Go to the start" }).click();
  await expect(page).toHaveURL(/\/(welcome)?$/);
});

for (const colorScheme of ["light", "dark"] as const) {
  test.describe(`in ${colorScheme} mode`, () => {
    test.use({ colorScheme });

    test("the not-found page has no accessibility violations", async ({ page }) => {
      await page.goto(UNKNOWN_ADDRESS);
      await expect(page.getByRole("heading", { level: 1 })).toBeVisible();

      const { violations } = await new AxeBuilder({ page }).withTags(WCAG_AA_TAGS).analyze();

      expect(violations).toEqual([]);
    });
  });
}
