import AxeBuilder from "@axe-core/playwright";
import { expect, type Page } from "@playwright/test";

const SCHEMES = ["light", "dark"] as const;
const TAB_PRESSES = 40;

/** What a screen has wrong, by the checks of the acceptance list that a browser can make. Each is a line of words. */
async function problemsOn(page: Page): Promise<readonly string[]> {
  return page.evaluate(() => {
    const problems: string[] = [];
    const MINIMUM_TARGET = 47.5;
    const WELSH_MARKERS = /[ŵŷŴŶ]|dyfal donc|Dechrau|Dal ati/i;

    const visible = (element: Element) => {
      const box = element.getBoundingClientRect();
      const style = getComputedStyle(element);

      return box.width > 0 && box.height > 0 && style.visibility !== "hidden" && style.display !== "none";
    };
    const describe = (element: Element) =>
      `${element.tagName.toLowerCase()} "${element.textContent.trim().slice(0, 30)}"`;
    const isRed = (colour: string) => {
      const match = /rgba?\((\d+), (\d+), (\d+)/.exec(colour);

      return match !== null && Number(match[1]) >= 150 && Number(match[2]) <= 100 && Number(match[3]) <= 100;
    };

    for (const element of document.querySelectorAll("body *")) {
      if (!visible(element)) {
        continue;
      }

      const style = getComputedStyle(element);

      if (style.boxShadow !== "none") {
        problems.push(`shadow on ${describe(element)}`);
      }

      if (style.backgroundImage !== "none") {
        problems.push(`background image on ${describe(element)}`);
      }

      if ([style.color, style.backgroundColor, style.borderTopColor, style.outlineColor].some(isRed)) {
        problems.push(`red on ${describe(element)}`);
      }

      const own = [...element.childNodes]
        .filter((node) => node.nodeType === Node.TEXT_NODE)
        .map((node) => node.textContent ?? "")
        .join(" ");

      if (WELSH_MARKERS.test(own) && element.closest("[lang=cy]") === null) {
        problems.push(`Welsh without lang="cy" in ${describe(element)}`);
      }
    }

    const targets = document.querySelectorAll(
      "a[href], button, [role=button], select, textarea, input:not([type=hidden])",
    );

    for (const target of targets) {
      if (!visible(target) || target.closest("[aria-hidden=true]") !== null) {
        continue;
      }

      const choice = target instanceof HTMLInputElement && ["checkbox", "radio"].includes(target.type);
      const measured = choice ? (target.closest("label") ?? target) : target;
      const { height } = measured.getBoundingClientRect();

      if (height < MINIMUM_TARGET) {
        problems.push(`target ${Math.round(height)} px tall: ${describe(target)}`);
      }
    }

    return problems;
  });
}

/** Tabs through the screen, and says which stops have no visible focus ring. */
async function stopsWithoutRing(page: Page): Promise<readonly string[]> {
  const missing: string[] = [];
  const seen = new Set<string>();

  await page.evaluate(() => {
    (document.activeElement as HTMLElement | null)?.blur();
  });

  for (let press = 0; press < TAB_PRESSES; press += 1) {
    await page.keyboard.press("Tab");

    const stop = await page.evaluate(() => {
      const element = document.activeElement;

      if (element === null || element === document.body) {
        return null;
      }

      let ringed = false;

      for (let ancestor: Element | null = element, depth = 0; ancestor !== null && depth < 4; depth += 1) {
        const style = getComputedStyle(ancestor);

        if (style.outlineStyle !== "none" && Number.parseFloat(style.outlineWidth) > 0) {
          ringed = true;
        }

        ancestor = ancestor.parentElement;
      }

      const name = `${element.tagName.toLowerCase()} "${(element.getAttribute("aria-label") ?? element.textContent).trim().slice(0, 30)}"`;

      return { name: `${name} #${[...document.querySelectorAll("*")].indexOf(element)}`, ringed };
    });

    if (stop === null || seen.has(stop.name)) {
      break;
    }

    seen.add(stop.name);

    if (!stop.ringed) {
      missing.push(stop.name);
    }
  }

  return missing;
}

/** Waits for what is sliding or fading to finish, so a colour is measured when it has settled. A pulse never finishes and is left. */
async function settle(page: Page): Promise<void> {
  await page.waitForFunction(() =>
    document
      .getAnimations()
      .every(
        (animation) =>
          animation.playState !== "running" ||
          animation.effect?.getComputedTiming().iterations === Number.POSITIVE_INFINITY,
      ),
  );
}

/**
 * Checks the screen that is showing, in light and then dark: no violations of WCAG 2 AA, nothing
 * the design rules out, every target 48 px, and a focus ring at every stop of the keyboard.
 */
export async function inspectScreen(page: Page, name: string): Promise<void> {
  for (const colorScheme of SCHEMES) {
    await page.emulateMedia({ colorScheme });
    await settle(page);

    const violations = (await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa"]).analyze()).violations;

    expect(
      violations.map(
        (violation) => `${violation.id}: ${violation.nodes.map((node) => node.target.join(" ")).join(", ")}`,
      ),
      `${name} in ${colorScheme}: accessibility`,
    ).toEqual([]);
    expect(await problemsOn(page), `${name} in ${colorScheme}: design rules`).toEqual([]);
    expect(await stopsWithoutRing(page), `${name} in ${colorScheme}: focus rings`).toEqual([]);
  }
}

/** The interactive elements that are too small to press, for a screen on a phone. */
export async function smallTargets(page: Page): Promise<readonly string[]> {
  return (await problemsOn(page)).filter((problem) => problem.startsWith("target"));
}
