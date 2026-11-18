import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

import { TEST_IDS } from "../src/config/test-ids";
import { chooseFromMenu, requireStack, startAsGuest, startButton, startLesson } from "./helpers";

const AUDIO_PATH = /\/api\/exercises\/.+\/audio\/(?<track>.+)$/;

test.beforeEach(async ({ request }) => {
  await requireStack(request);
});

test("a learner hears an exercise, marks it missed and moves on", async ({ page }) => {
  const clips: { status: number; track: string | undefined }[] = [];

  page.on("response", (response) => {
    const match = AUDIO_PATH.exec(response.url());

    if (match) {
      clips.push({ status: response.status(), track: match.groups?.track });
    }
  });

  await startAsGuest(page);
  await startLesson(page);

  const english = page.getByTestId(TEST_IDS.english);
  const welsh = page.getByTestId(TEST_IDS.welsh);
  const missedIt = page.getByTestId(TEST_IDS.missedIt);

  await expect(english).not.toHaveText("");
  await expect(welsh).toHaveText("");

  const missedItBox = await missedIt.boundingBox();

  const criticalViolations = (await new AxeBuilder({ page }).analyze()).violations.filter(
    (violation) => violation.impact === "critical",
  );

  expect(criticalViolations).toEqual([]);

  await expect(welsh).not.toHaveText("", { timeout: 30_000 });
  expect(await missedIt.boundingBox()).toEqual(missedItBox);

  await page.keyboard.press("m");
  await expect(missedIt).toContainText("Marked");

  const outcome = await page.waitForResponse(
    (response) => response.url().endsWith("/outcomes") && response.request().method() === "POST",
    { timeout: 30_000 },
  );

  expect(outcome.request().postDataJSON()).toMatchObject({ outcome: "missed_it" });
  expect(await outcome.json()).toMatchObject({ recorded: true });
  expect(clips.slice(0, 3).map((clip) => clip.track)).toEqual(
    expect.arrayContaining(["english", "welsh/standard", "welsh/slow"]),
  );
  expect(clips.every((clip) => clip.status === 200)).toBe(true);

  // The next exercise's clips are fetched, and its track plays, with nobody tapping anything
  await expect.poll(() => clips.length, { timeout: 30_000 }).toBeGreaterThanOrEqual(6);

  await expect(welsh).toHaveText("");
  await expect(english).not.toHaveText("");

  // The first exercise has moved on, so it is the sentence to report
  await chooseFromMenu(page, "button", "Report a problem");
  // A dialog hides the page behind it from the accessibility tree, but the lesson is paused behind it
  await expect(page.getByRole("button", { includeHidden: true, name: /^Resume/ })).toBeVisible();

  const dialog = page.getByRole("dialog", { name: "Report a problem" });

  await expect(dialog.getByRole("radio")).toHaveCount(2);
  await dialog.getByLabel("What kind of problem is it?").click();
  await page.getByRole("option", { name: "Sounds wrong when spoken" }).click();
  await dialog.getByLabel("What is wrong?").fill("The voice says it oddly");

  const reportRequest = page.waitForRequest(
    (request) => request.url().endsWith("/me/problem-reports") && request.method() === "POST",
  );
  const reportResponse = page.waitForResponse(
    (response) => response.url().endsWith("/me/problem-reports") && response.request().method() === "POST",
  );

  await dialog.getByRole("button", { name: "Send" }).click();

  expect((await reportRequest).postDataJSON()).toEqual({
    category: "sounds_wrong",
    description: "The voice says it oddly",
    exercise_id: expect.any(String),
    item_id: null,
    source: "lesson",
  });
  expect((await reportResponse).status()).toBe(204);
  await expect(dialog.getByText("Thanks, it's been sent")).toBeVisible();

  await dialog.getByRole("button", { name: "Close" }).click();
  await expect(dialog).toBeHidden();
  await expect(page.getByRole("button", { name: /^Resume/ })).toBeVisible();

  await page.getByRole("button", { name: /^Resume/ }).click();
  await expect(page.getByRole("button", { name: /^Pause/ })).toBeVisible();
});

test("Stop for now returns to rest, and Space starts the lesson again from there", async ({ page }) => {
  await startAsGuest(page);
  await startLesson(page);
  await expect(page.getByTestId(TEST_IDS.english)).not.toHaveText("");

  await chooseFromMenu(page, "button", "Stop for now");
  await expect(startButton(page)).toBeVisible();
  await expect(page.getByTestId(TEST_IDS.english)).toHaveCount(0);

  await page.keyboard.press("Space");
  await expect(page.getByTestId(TEST_IDS.english)).not.toHaveText("");
});

test("stopping while the next exercise is still loading leaves the lesson at rest", async ({ page }) => {
  const SLOW_RESPONSE_MILLISECONDS = 1500;

  await startAsGuest(page);
  await page.route("**/api/me/next", async (route) => {
    await new Promise((resolve) => setTimeout(resolve, SLOW_RESPONSE_MILLISECONDS));
    await route.continue();
  });

  await startLesson(page);
  await chooseFromMenu(page, "button", "Stop for now");
  await page.waitForResponse((response) => response.url().endsWith("/me/next"));
  await page.waitForTimeout(SLOW_RESPONSE_MILLISECONDS);

  await expect(startButton(page)).toBeVisible();
  await expect(page.getByTestId(TEST_IDS.english)).toHaveCount(0);
});

test("the old lesson address leads to the home screen, where the lesson starts", async ({ page }) => {
  await startAsGuest(page);
  await page.goto("/learn");

  await expect(page).toHaveURL(/\/$/);
  await expect(startButton(page)).toBeVisible();
});

test("the menu holds the lesson, ignores its shortcuts, and leaves it paused when closed", async ({ page }) => {
  await startAsGuest(page);
  await startLesson(page);
  await expect(page.getByTestId(TEST_IDS.english)).not.toHaveText("");

  const menuButton = page.getByRole("button", { name: "Menu" });

  await menuButton.click();

  const menu = page.getByRole("dialog", { name: "Menu" });

  await expect(menu.getByRole("link", { name: "Look something up" })).toBeVisible();
  await expect(menu.getByRole("button", { name: "Report a problem" })).toBeVisible();
  await expect(menu.getByRole("link", { name: "Settings" })).toBeVisible();
  await expect(menu.getByRole("link", { name: "Account" })).toBeVisible();
  await expect(menu.getByRole("button", { name: "Stop for now" })).toBeVisible();

  // The lesson pauses as soon as it can, which is after its audio has started
  await expect(page.getByRole("button", { includeHidden: true, name: /^Resume/ })).toBeVisible();

  // Space would resume it, if the shortcuts were not stood down
  await page.keyboard.press("Space");
  await page.keyboard.press("Escape");
  await expect(menu).toBeHidden();
  await expect(menuButton).toBeFocused();
  await expect(page.getByRole("button", { name: /^Resume/ })).toBeVisible();
});

test("at rest the menu has no way to stop", async ({ page }) => {
  await startAsGuest(page);
  await page.getByRole("button", { name: "Menu" }).click();

  const menu = page.getByRole("dialog", { name: "Menu" });

  await expect(menu.getByRole("link", { name: "Look something up" })).toBeVisible();
  await expect(menu.getByRole("button", { name: "Stop for now" })).toHaveCount(0);
  await expect(menu).toContainText("On headphones and the lock screen");
});

test("the captions follow the exercise, the Welsh appears with the second voice, and Next ends the wait", async ({
  page,
}) => {
  await startAsGuest(page);
  await startLesson(page);

  const caption = page.getByTestId(TEST_IDS.caption);
  const welsh = page.getByTestId(TEST_IDS.welsh);
  const outcome = page.waitForResponse(
    (response) => response.url().endsWith("/outcomes") && response.request().method() === "POST",
    { timeout: 40_000 },
  );

  await expect(caption).toHaveText(/^(Listen|Something new\. Have a guess\.)$/, { timeout: 15_000 });
  await expect(caption).toHaveText(/^(Say it in Welsh|Something new\. Have a guess\.)$/, { timeout: 15_000 });
  await expect(caption).toHaveText("Now listen", { timeout: 15_000 });
  await expect(welsh).toHaveText("");

  await expect(caption).toHaveText("Once more, slowly", { timeout: 15_000 });
  await expect(welsh).not.toHaveText("");

  await expect(caption).toHaveText("Next one coming up", { timeout: 15_000 });
  await page.getByRole("button", { name: "Next" }).click();
  expect((await outcome).request().postDataJSON()).toMatchObject({ outcome: "got_it" });
});

test("the beat row has a block for each Welsh word and three more, and opens when the Welsh shows", async ({
  page,
}) => {
  await startAsGuest(page);
  await startLesson(page);

  const row = page.getByTestId(TEST_IDS.beatRow);
  const welsh = page.getByTestId(TEST_IDS.welsh);

  await expect(page.getByTestId(TEST_IDS.english)).not.toHaveText("");
  await expect(row).toHaveAttribute("data-opened", "false");
  await expect(welsh).toHaveText("");

  await expect(welsh).not.toHaveText("", { timeout: 30_000 });
  await expect(row).toHaveAttribute("data-opened", "true");

  const words = (await welsh.innerText()).trim().split(/\s+/).length;

  await expect(row.locator("> *")).toHaveCount(words + 3);
});
