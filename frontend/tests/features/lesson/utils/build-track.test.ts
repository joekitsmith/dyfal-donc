import { describe, expect, it } from "vitest";

import type { WelshPlayback } from "@/features/lesson/types";

import { layoutTrack } from "@/features/lesson/utils/build-track";
import { phaseAt } from "@/features/lesson/utils/phase-at";
import { tailStart } from "@/features/lesson/utils/tail-start";

const RATE = 100;

function clip(seconds: number, value: number) {
  return { pcm: new Int16Array(seconds * RATE).fill(value), sampleRate: RATE };
}

function layout(welshPlayback: WelshPlayback, sampleRate = RATE) {
  return layoutTrack({
    clips: {
      english: clip(2, 1),
      welsh_slow: clip(4, 3),
      welsh_standard: { ...clip(3, 2), sampleRate },
    },
    thinkSeconds: 5,
    welshPlayback,
  });
}

describe("layoutTrack", () => {
  it("puts both Welsh clips between silences, and a tail after the outcome window", () => {
    const { samples, timeline } = layout("both");

    expect(timeline).toEqual([
      { phase: "playing_english", startsAt: 0 },
      { phase: "thinking", startsAt: 2 },
      { phase: "playing_welsh_standard", startsAt: 7 },
      { phase: "between_welsh", startsAt: 10 },
      { phase: "playing_welsh_slow", startsAt: 11.5 },
      { phase: "awaiting_outcome", startsAt: 15.5 },
      { phase: "submitting", startsAt: 17.5 },
    ]);
    expect(samples.length).toBe((17.5 + 10) * RATE);
    expect(samples[0]).toBe(1);
    expect(samples[2 * RATE]).toBe(0);
    expect(samples[7 * RATE]).toBe(2);
    expect(samples[11.5 * RATE]).toBe(3);
  });

  it("leaves out the Welsh and the gap the setting does not play", () => {
    expect(layout("standard").timeline.map((entry) => entry.phase)).toEqual([
      "playing_english",
      "thinking",
      "playing_welsh_standard",
      "awaiting_outcome",
      "submitting",
    ]);
    expect(layout("slow").timeline.map((entry) => entry.phase)).toEqual([
      "playing_english",
      "thinking",
      "playing_welsh_slow",
      "awaiting_outcome",
      "submitting",
    ]);
  });

  it("refuses clips at different rates, and a clip that is missing", () => {
    expect(() => layout("both", 200)).toThrow("different sample rates");
    expect(() => layoutTrack({ clips: { english: clip(1, 1) }, thinkSeconds: 1, welshPlayback: "standard" })).toThrow(
      "welsh_standard clip is missing",
    );
  });
});

describe("phaseAt", () => {
  it("is the last phase that has started", () => {
    const { timeline } = layout("both");

    expect(phaseAt(timeline, 0)).toBe("playing_english");
    expect(phaseAt(timeline, 6.99)).toBe("thinking");
    expect(phaseAt(timeline, 7)).toBe("playing_welsh_standard");
    expect(phaseAt(timeline, 16)).toBe("awaiting_outcome");
    expect(phaseAt(timeline, 17.5)).toBe("submitting");
    expect(phaseAt(timeline, 999)).toBe("submitting");
  });
});

describe("tailStart", () => {
  it("is where the outcome window ends", () => {
    expect(tailStart(layout("both").timeline)).toBe(17.5);
    expect(tailStart([])).toBe(0);
  });
});
