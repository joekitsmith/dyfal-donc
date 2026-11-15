export const SETTINGS_QUERY_KEY = ["settings"] as const;

export const THINK_MULTIPLIER_MINIMUM = 0.5;
export const THINK_MULTIPLIER_MAXIMUM = 3;
export const THINK_MULTIPLIER_STEP = 0.25;

export const WELSH_PLAYBACK_OPTIONS = [
  { label: "Standard, then slow", value: "both" },
  { label: "Slow only", value: "slow" },
  { label: "Standard only", value: "standard" },
] as const;
