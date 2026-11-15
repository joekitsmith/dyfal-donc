import { type APIRequestContext, expect, type Page } from "@playwright/test";

const FAST_THINK_MULTIPLIER = "0.5";
const LONG_CLIP_SECONDS = 0.2;

/** Counts the clips that play to the end. The silent clip that unlocks audio is too short to count. */
export async function countClipsEnded(page: Page): Promise<number> {
  return page.evaluate(() => (window as unknown as Record<string, number>).__clipsEnded ?? 0);
}

export async function instrumentAudio(page: Page): Promise<void> {
  await page.addInitScript((longClipSeconds) => {
    const counter = window as unknown as Record<string, number>;
    const watched = new WeakSet<HTMLMediaElement>();
    // Patching the prototype is the point, and `play.call` below supplies `this`
    // eslint-disable-next-line @typescript-eslint/unbound-method
    const play = HTMLMediaElement.prototype.play;

    counter.__clipsEnded = 0;

    HTMLMediaElement.prototype.play = function (this: HTMLMediaElement) {
      if (!watched.has(this)) {
        watched.add(this);
        this.addEventListener("ended", () => {
          if (this.duration > longClipSeconds) {
            counter.__clipsEnded = (counter.__clipsEnded ?? 0) + 1;
          }
        });
      }

      return play.call(this);
    };
  }, LONG_CLIP_SECONDS);
}

export async function requireStack(request: APIRequestContext): Promise<void> {
  const response = await request.get("/api/health").catch(() => undefined);

  if (response?.ok() !== true) {
    throw new Error(
      "The API is not reachable. Run `make stack-up`, and `poetry run poe db-create` the first time, then try again",
    );
  }
}

/** A shorter think time keeps a whole lesson under half a minute. */
export async function speedUpThinking(page: Page): Promise<void> {
  await page.addInitScript((multiplier) => {
    window.localStorage.setItem("dyfal-donc.think-time-multiplier", multiplier);
  }, FAST_THINK_MULTIPLIER);
}

/** Starts as a guest from the front door, as a new visitor would. */
export async function startAsGuest(page: Page): Promise<void> {
  await page.goto("/");
  await page.getByRole("button", { name: "Try it now" }).click();
  await expect(page).toHaveURL(/\/learn$/);
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
