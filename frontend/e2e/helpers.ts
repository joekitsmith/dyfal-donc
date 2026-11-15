import type { APIRequestContext, Page } from "@playwright/test";

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
