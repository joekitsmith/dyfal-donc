import type { ClipTrack, PositionPhase, Timeline, WelshPlayback } from "../types";

import { BETWEEN_WELSH_SECONDS, OUTCOME_WINDOW_SECONDS, TAIL_SECONDS } from "../constants";
import { encodeWav, type WavClip } from "./wav";

export type BuiltTrack = {
  readonly blob: Blob;
  readonly timeline: Timeline;
};

export type TrackLayout = {
  readonly sampleRate: number;
  readonly samples: Int16Array;
  readonly timeline: Timeline;
};

export type TrackSource = {
  /** The clips that play: English, and the Welsh ones the setting asks for. */
  readonly clips: Readonly<Partial<Record<ClipTrack, WavClip>>>;
  readonly thinkSeconds: number;
  readonly welshPlayback: WelshPlayback;
};

type Segment = ({ readonly clip: WavClip } | { readonly silenceSeconds: number }) & { readonly phase: PositionPhase };

/**
 * One exercise as one piece of audio: the English, silence for the think time, the Welsh, and
 * silence for the outcome window and then for the tail. The timeline says where each phase starts.
 */
export function buildTrack(source: TrackSource): BuiltTrack {
  const { sampleRate, samples, timeline } = layoutTrack(source);

  return { blob: encodeWav(samples, sampleRate), timeline };
}

export function layoutTrack({ clips, thinkSeconds, welshPlayback }: TrackSource): TrackLayout {
  const english = requireClip(clips, "english");
  const { sampleRate } = english;
  const segments: Segment[] = [
    { clip: english, phase: "playing_english" },
    { phase: "thinking", silenceSeconds: thinkSeconds },
  ];

  if (welshPlayback !== "slow") {
    segments.push({ clip: requireClip(clips, "welsh_standard"), phase: "playing_welsh_standard" });
  }

  if (welshPlayback === "both") {
    segments.push({ phase: "between_welsh", silenceSeconds: BETWEEN_WELSH_SECONDS });
  }

  if (welshPlayback !== "standard") {
    segments.push({ clip: requireClip(clips, "welsh_slow"), phase: "playing_welsh_slow" });
  }

  segments.push(
    { phase: "awaiting_outcome", silenceSeconds: OUTCOME_WINDOW_SECONDS },
    { phase: "submitting", silenceSeconds: TAIL_SECONDS },
  );

  const parts = segments.map((segment) =>
    "clip" in segment ? segment.clip.pcm : new Int16Array(Math.round(segment.silenceSeconds * sampleRate)),
  );

  for (const segment of segments) {
    if ("clip" in segment && segment.clip.sampleRate !== sampleRate) {
      throw new Error("The clips have different sample rates");
    }
  }

  const samples = new Int16Array(parts.reduce((total, part) => total + part.length, 0));
  const timeline: { phase: PositionPhase; startsAt: number }[] = [];
  let offset = 0;

  for (const [index, part] of parts.entries()) {
    timeline.push({ phase: segments[index]?.phase ?? "submitting", startsAt: offset / sampleRate });
    samples.set(part, offset);
    offset += part.length;
  }

  return { sampleRate, samples, timeline };
}

function requireClip(clips: TrackSource["clips"], track: ClipTrack): WavClip {
  const clip = clips[track];

  if (clip === undefined) {
    throw new Error(`The ${track} clip is missing`);
  }

  return clip;
}
