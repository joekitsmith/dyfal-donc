import { expect, test } from "@playwright/test";

import { TEST_IDS } from "../src/config/test-ids";
import { chooseFromMenu, requireStack, startAsGuest, startLesson } from "./helpers";
import { inspectScreen } from "./inspect";

test.beforeEach(async ({ request }) => {
  await requireStack(request);
});

test("every screen passes the accessibility check and the design's rules, in light and dark, and nothing leaves the site", async ({
  baseURL,
  page,
}) => {
  const foreign: string[] = [];
  const origin = new URL(baseURL ?? "http://localhost").origin;

  page.on("request", (request) => {
    const { origin: requested, protocol } = new URL(request.url());

    if (["http:", "https:"].includes(protocol) && requested !== origin) {
      foreign.push(request.url());
    }
  });

  // Signed out
  await page.goto("/welcome");
  await expect(page.getByRole("button", { name: "Try it now" })).toBeVisible();
  await inspectScreen(page, "Welcome");

  await page.goto("/recover");
  await expect(page.getByLabel("Recovery code")).toBeVisible();
  await inspectScreen(page, "Recover");

  await page.goto("/there-is-nothing-here");
  await expect(page.getByRole("heading", { name: "This page isn't here" })).toBeVisible();
  await inspectScreen(page, "Not found");

  // A new learner
  await startAsGuest(page);
  await inspectScreen(page, "Home");

  await page.getByRole("button", { name: "Menu" }).click();
  await expect(page.getByRole("dialog", { name: "Menu" })).toBeVisible();
  await inspectScreen(page, "Menu");
  await page.keyboard.press("Escape");

  await chooseFromMenu(page, "button", "Report a problem");
  await expect(page.getByRole("dialog", { name: "Report a problem" })).toBeVisible();
  await inspectScreen(page, "Report a problem");
  await page.keyboard.press("Escape");

  for (const [path, heading] of [
    ["/account", "Account"],
    ["/settings", "Settings"],
    ["/course", "Everything you've met"],
  ] as const) {
    await page.goto(path);
    await expect(page.getByRole("heading", { level: 1, name: heading })).toBeVisible();
    await inspectScreen(page, heading);
  }

  // A lesson, once the Welsh has shown
  await page.goto("/");
  await startLesson(page);
  await expect(page.getByTestId(TEST_IDS.english)).not.toHaveText("");
  await inspectScreen(page, "Lesson, English");
  await expect(page.getByTestId(TEST_IDS.welsh)).not.toHaveText("", { timeout: 30_000 });
  await inspectScreen(page, "Lesson, Welsh shown");

  await page.keyboard.press("m");
  await expect(page.getByTestId(TEST_IDS.missedIt)).toContainText("Marked");
  await inspectScreen(page, "Lesson, marked");
  await page.waitForResponse((response) => response.url().endsWith("/outcomes"), { timeout: 30_000 });

  await chooseFromMenu(page, "button", "Look something up");
  await expect(page.getByRole("dialog", { name: "Everything you've met" })).toBeVisible();
  await inspectScreen(page, "Course over the lesson");
  await page.keyboard.press("Escape");

  // After a session
  await chooseFromMenu(page, "button", "Stop for now");
  await expect(page.getByRole("region", { name: "Latest session" })).toBeVisible();
  await inspectScreen(page, "Home after a session");

  await page.getByRole("link", { name: "Look back" }).click();
  await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
  await inspectScreen(page, "Summary");

  await page.goto("/course");
  await page.getByRole("region", { name: "Words" }).getByRole("link").first().click();
  await expect(page.getByRole("button", { name: "Hear it" })).toBeVisible();
  await inspectScreen(page, "A word");

  expect(foreign, "requests to other sites").toEqual([]);
});

test("with reduced motion nothing on the lesson pulses or runs for long", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await startAsGuest(page);
  await startLesson(page);
  await expect(page.getByTestId(TEST_IDS.welsh)).not.toHaveText("", { timeout: 30_000 });

  const motion = await page.evaluate(() =>
    [...document.querySelectorAll("body *")].flatMap((element) => {
      const style = getComputedStyle(element);
      const pulsing = style.animationName !== "none" && style.animationIterationCount === "infinite";
      // A fade may stay, if it is quick
      const slow = style.animationName !== "none" && Number.parseFloat(style.animationDuration) > 0.12;

      return pulsing || slow ? [element.tagName.toLowerCase()] : [];
    }),
  );

  expect(motion).toEqual([]);
});

test("the Welsh letters ŵ and ŷ are drawn in the product's font", async ({ page }) => {
  await startAsGuest(page);

  const drawn = await page.evaluate(async () => {
    const faces = await document.fonts.load('600 30px "Geologica Variable"', "ŵŷŴŶâêîôû");

    return { check: document.fonts.check('600 30px "Geologica Variable"', "ŵŷŴŶ"), faces: faces.length };
  });

  expect(drawn.faces).toBeGreaterThan(0);
  expect(drawn.check).toBe(true);
});
