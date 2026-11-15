import { type APIRequestContext, expect, type Page } from "@playwright/test";

const FAST_THINK_MULTIPLIER = 0.5;

export async function requireStack(request: APIRequestContext): Promise<void> {
  const response = await request.get("/api/health").catch(() => undefined);

  if (response?.ok() !== true) {
    throw new Error(
      "The API is not reachable. Run `make stack-up`, and `poetry run poe db-create` the first time, then try again",
    );
  }
}

/** A shorter think time keeps a whole lesson under half a minute. The learner has to be signed in already. */
async function speedUpThinking(page: Page, settings: Record<string, unknown> = {}): Promise<void> {
  const origin = new URL(page.url()).origin;
  const response = await page.request.patch("/api/me/settings", {
    data: { think_time_multiplier: FAST_THINK_MULTIPLIER, ...settings },
    headers: { Origin: origin },
  });

  expect(response.ok()).toBe(true);
  // Screens read the settings when they loaded
  await page.reload();
}

/** Opens the lesson from the home screen, which is where signing in leaves a person. */
export async function openLesson(page: Page): Promise<void> {
  await page.getByRole("link", { name: /^(Start|Continue) learning$/ }).click();
  await expect(page).toHaveURL(/\/learn$/);
}

/** Starts as a guest from the front door, as a new visitor would, and opens the lesson with the quick think time. */
export async function startAsGuest(page: Page, settings: Record<string, unknown> = {}): Promise<void> {
  await page.goto("/");
  await page.getByRole("button", { name: "Try it now" }).click();
  await expect(page).toHaveURL(/\/$/);
  await speedUpThinking(page, settings);
  await openLesson(page);
}

/**
 * A software passkey device in the browser, so the real ceremonies run with nobody to approve them.
 * `replace` swaps it for a new one, as if the old device were lost.
 */
export async function installPasskeyDevice(page: Page): Promise<{ readonly replace: () => Promise<void> }> {
  const session = await page.context().newCDPSession(page);

  await session.send("WebAuthn.enable");

  const add = async () =>
    (
      await session.send("WebAuthn.addVirtualAuthenticator", {
        options: {
          automaticPresenceSimulation: true,
          hasResidentKey: true,
          hasUserVerification: true,
          isUserVerified: true,
          protocol: "ctap2",
          transport: "internal",
        },
      })
    ).authenticatorId;
  let authenticatorId = await add();

  return {
    replace: async () => {
      await session.send("WebAuthn.removeVirtualAuthenticator", { authenticatorId });
      authenticatorId = await add();
    },
  };
}

/** Adds a passkey to a guest from the account screen, and returns the first recovery code it was given. */
export async function saveProgressAndKeepFirstCode(page: Page): Promise<string> {
  await page.getByRole("link", { name: "Account" }).click();
  await page.getByRole("button", { name: "Add a passkey" }).click();

  const dialog = page.getByRole("dialog", { name: "Save your recovery codes" });
  const code = (await dialog.getByRole("listitem").first().textContent()) ?? "";

  await dialog.getByLabel("I have saved these codes").check();
  await dialog.getByRole("button", { name: "Done" }).click();
  await expect(page.getByText("You are signed in with a passkey.")).toBeVisible();

  return code;
}
