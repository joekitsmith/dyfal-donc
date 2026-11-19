import { expect, test } from "@playwright/test";

import { TEST_IDS } from "../src/config/test-ids";
import { chooseFromMenu, requireStack, startAsGuest, startButton, startLesson } from "./helpers";

test.beforeEach(async ({ request }) => {
  await requireStack(request);
});

test("after a session the home screen recaps it and the summary lets a missed exercise be played again", async ({
  page,
}) => {
  await startAsGuest(page);
  await startLesson(page);
  await expect(page.getByTestId(TEST_IDS.welsh)).not.toHaveText("", { timeout: 30_000 });
  await page.keyboard.press("m");
  await page.waitForResponse((response) => response.url().endsWith("/outcomes"), { timeout: 30_000 });
  await expect(page.getByTestId(TEST_IDS.sessionClock)).toBeVisible();

  await chooseFromMenu(page, "button", "Stop for now");

  const recap = page.getByRole("region", { name: "Latest session" });

  await expect(recap).toContainText("This session so far · 1 sentence");
  await expect(startButton(page)).toContainText("Dal ati");

  await recap.getByRole("link", { name: "Look back" }).click();
  await expect(page.getByRole("heading", { name: "This session so far" })).toBeVisible();
  await expect(page.getByText("1 sentence in under a minute, and still going.")).toBeVisible();
  await expect(page.getByRole("region", { name: "New" }).getByRole("link")).toHaveCount(1);

  const missed = page.getByRole("region", { name: "Sentences you marked" });
  const clip = page.waitForResponse((response) => response.url().endsWith("/audio/welsh/standard"));

  await missed.getByRole("button", { name: /^Play (?!.*slowly)/ }).click();
  expect((await clip).status()).toBe(200);

  await missed.getByRole("button", { name: /^Report / }).click();

  const dialog = page.getByRole("dialog", { name: "Report a problem" });
  const reportRequest = page.waitForRequest(
    (request) => request.url().endsWith("/me/problem-reports") && request.method() === "POST",
  );

  // One sentence is offered, so there is nothing to choose between
  await expect(dialog.getByRole("radio")).toHaveCount(0);
  await dialog.getByLabel("What kind of problem is it?").selectOption({ label: "Other" });
  await dialog.getByLabel("What is wrong?").fill("Something is off");
  await dialog.getByRole("button", { name: "Send" }).click();

  expect((await reportRequest).postDataJSON()).toMatchObject({
    category: "other",
    exercise_id: expect.any(String),
    source: "summary",
  });
  await expect(dialog.getByText("Thanks, it's been sent")).toBeVisible();
  // The dialog has a close button at the top as well as the one that answers the thanks
  await dialog.getByRole("button", { name: "Close" }).last().click();
  await expect(dialog).toBeHidden();

  await page.getByRole("link", { name: "Back to the lesson" }).click();
  await expect(page).toHaveURL(/\/$/);
});

test("a session that does not exist says so", async ({ page }) => {
  await startAsGuest(page);

  await page.goto("/learning-sessions/99");

  await expect(page.getByText("We couldn't find that session.")).toBeVisible();
});
