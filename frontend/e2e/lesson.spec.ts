import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

import { TEST_IDS } from "../src/config/test-ids";
import { countClipsEnded, instrumentAudio, requireStack, speedUpThinking } from "./helpers";

const AUDIO_PATH = /\/api\/exercises\/.+\/audio\/(?<track>.+)$/;

test.beforeEach(async ({ page, request }) => {
  await requireStack(request);
  await speedUpThinking(page);
  await instrumentAudio(page);
});

test("a learner hears an exercise, marks it missed and moves on", async ({ page }) => {
  const clips: { status: number; track: string | undefined }[] = [];

  page.on("response", (response) => {
    const match = AUDIO_PATH.exec(response.url());

    if (match) {
      clips.push({ status: response.status(), track: match.groups?.track });
    }
  });

  await page.goto("/");
  const progress = page.getByTestId(TEST_IDS.progress);

  await expect(progress).toContainText("Introduced: 0 of");
  await page.getByRole("button", { exact: true, name: "Start" }).click();

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
    expect.arrayContaining(["english", "welsh", "welsh-slow"]),
  );
  expect(clips.every((clip) => clip.status === 200)).toBe(true);
  expect(await countClipsEnded(page)).toBeGreaterThanOrEqual(3);

  await expect(progress).toContainText("Introduced: 1 of");
  await expect(welsh).toHaveText("");
  await expect(english).not.toHaveText("");
});
