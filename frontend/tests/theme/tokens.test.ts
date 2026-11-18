import { describe, expect, it } from "vitest";

import { COLOURS } from "@/theme/tokens";

type ColourName = keyof typeof COLOURS.light;

const TEXT_RATIO = 4.5;
const OUTLINE_RATIO = 3;

/** The foreground, the background it sits on, and the ratio DESIGN.md section 2.1 needs between them. */
const PAIRS: readonly (readonly [ColourName, ColourName, number])[] = [
  ["ink", "ground", TEXT_RATIO],
  ["ink", "surface", TEXT_RATIO],
  ["muted", "ground", TEXT_RATIO],
  ["muted", "surface", TEXT_RATIO],
  ["inverse-fg", "inverse-bg", TEXT_RATIO],
  ["line", "ground", OUTLINE_RATIO],
  ["line", "surface", OUTLINE_RATIO],
  ["accent", "ground", OUTLINE_RATIO],
  ["accent", "surface", OUTLINE_RATIO],
];

function luminance(hex: string): number {
  const [red = 0, green = 0, blue = 0] = [1, 3, 5].map((start) => {
    const channel = Number.parseInt(hex.slice(start, start + 2), 16) / 255;

    return channel <= 0.039_28 ? channel / 12.92 : ((channel + 0.055) / 1.055) ** 2.4;
  });

  return 0.2126 * red + 0.7152 * green + 0.0722 * blue;
}

function contrast(foreground: string, background: string): number {
  const [lighter = 0, darker = 0] = [luminance(foreground), luminance(background)].toSorted((a, b) => b - a);

  return (lighter + 0.05) / (darker + 0.05);
}

describe.each(["light", "dark"] as const)("the %s colours", (scheme) => {
  it.each(PAIRS)("%s on %s is at least %d:1", (foreground, background, ratio) => {
    const colours = COLOURS[scheme];

    expect(contrast(colours[foreground], colours[background])).toBeGreaterThanOrEqual(ratio);
  });
});

describe("the two colour schemes", () => {
  it("define the same tokens", () => {
    expect(Object.keys(COLOURS.dark).toSorted()).toEqual(Object.keys(COLOURS.light).toSorted());
  });
});
