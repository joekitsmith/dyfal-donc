import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

import { TEST_IDS } from "../src/config/test-ids";
import { requireStack, startAsGuest, startLesson } from "./helpers";

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
  const progress = page.getByTestId(TEST_IDS.progress);

  await startLesson(page);
  await expect(progress).toContainText("Introduced: 0 of");

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
  await expect(missedIt).toHaveText("Marked as missed");

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

  await expect(progress).toContainText("Introduced: 1 of");
  await expect(welsh).toHaveText("");
  await expect(english).not.toHaveText("");

  // The first exercise has moved on, so it is the sentence to report
  await page.getByRole("button", { name: "Report a problem" }).click();
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

  await page.getByRole("button", { name: "Stop for now" }).click();
  await expect(page.getByRole("button", { name: /^(Start|Continue) learning$/ })).toBeVisible();
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
  await page.getByRole("button", { name: "Stop for now" }).click();
  await page.waitForResponse((response) => response.url().endsWith("/me/next"));
  await page.waitForTimeout(SLOW_RESPONSE_MILLISECONDS);

  await expect(page.getByRole("button", { name: /^(Start|Continue) learning$/ })).toBeVisible();
  await expect(page.getByTestId(TEST_IDS.english)).toHaveCount(0);
});

test("the old lesson address leads to the home screen, where the lesson starts", async ({ page }) => {
  await startAsGuest(page);
  await page.goto("/learn");

  await expect(page).toHaveURL(/\/$/);
  await expect(page.getByRole("button", { name: /^(Start|Continue) learning$/ })).toBeVisible();
});
