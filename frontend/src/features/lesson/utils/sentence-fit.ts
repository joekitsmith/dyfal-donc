import { ENGLISH_BOX_HEIGHT } from "@/components/screen-frame";

import { WELSH_TEXT_MAXIMUM_HEIGHT } from "../constants";

type Kind = "english" | "welsh";

type Target = { readonly element: HTMLElement; readonly kind: Kind };

const SIZES = [30, 26, 22, 20] as const;
const LARGEST_SIZE = 30;
const SMALLEST_SIZE = 20;
const BASE_FONT_SIZE = 16;

/**
 * Gives each sentence the largest size at which it fits its box. A sentence is measured as it is
 * shown, in the layout step before the screen is painted, so a long one is never seen at the wrong
 * size. It is measured again when the font arrives or the width changes, because both change where
 * the lines break.
 *
 * The size is set on the element itself. Nothing else in the lesson depends on it, so it does not
 * need a render of its own.
 */
export class SentenceFit {
  #englishSize: number = LARGEST_SIZE;
  readonly #targets = new Set<Target>();

  /** For the paragraph holding the English. Pass it as a ref. */
  english = (element: HTMLElement) => this.#attach({ element, kind: "english" });

  /** The Welsh uses the English's size, or a smaller one if it needs it, so the two look alike. */
  welsh = (element: HTMLElement) => this.#attach({ element, kind: "welsh" });

  /** Measures every sentence again, English first because the Welsh depends on its size. */
  refit(): void {
    const targets = [...this.#targets].sort((a, b) => Number(a.kind === "welsh") - Number(b.kind === "welsh"));

    for (const target of targets) {
      this.#fit(target);
    }
  }

  #attach(target: Target): () => void {
    let width = target.element.clientWidth;
    const observer = new ResizeObserver(() => {
      if (target.element.clientWidth !== width) {
        width = target.element.clientWidth;
        this.refit();
      }
    });

    this.#targets.add(target);
    this.#fit(target);
    observer.observe(target.element.parentElement ?? target.element);

    return () => {
      observer.disconnect();
      this.#targets.delete(target);
    };
  }

  #fit({ element, kind }: Target): void {
    const largest = kind === "english" ? LARGEST_SIZE : this.#englishSize;
    const maximumHeight = kind === "english" ? ENGLISH_BOX_HEIGHT : WELSH_TEXT_MAXIMUM_HEIGHT;
    const candidates = SIZES.filter((size) => size <= largest);
    const fitting = candidates.find((size) => {
      element.style.fontSize = remOf(size);

      return element.scrollHeight <= maximumHeight;
    });
    const size = fitting ?? SMALLEST_SIZE;

    element.style.fontSize = remOf(size);

    if (kind === "english") {
      this.#englishSize = size;
    }
  }
}

function remOf(size: number): string {
  return `${size / BASE_FONT_SIZE}rem`;
}
