import type { WELSH_PLAYBACK_OPTIONS } from "./constants";

export type UserSettings = {
  readonly thinkTimeMultiplier: number;
  readonly welshPlayback: WelshPlayback;
};

type WelshPlayback = (typeof WELSH_PLAYBACK_OPTIONS)[number]["value"];
