/** The design tokens of DESIGN.md section 2. Colour names are the custom property names without the --dd- prefix. */
export const COLOURS = {
  dark: {
    accent: "#3fb5a3",
    divider: "#353f45",
    ground: "#171c20",
    ink: "#e8ecee",
    "inverse-bg": "#e8ecee",
    "inverse-fg": "#171c20",
    line: "#74828a",
    muted: "#9aa7ae",
    scrim: "rgba(0, 0, 0, 0.6)",
    surface: "#262e33",
  },
  light: {
    accent: "#0f7a6c",
    divider: "#d5dade",
    ground: "#e4e7ea",
    ink: "#1a2126",
    "inverse-bg": "#1a2126",
    "inverse-fg": "#ffffff",
    line: "#6b7780",
    muted: "#4b575f",
    scrim: "rgba(26, 33, 38, 0.5)",
    surface: "#ffffff",
  },
} as const;

export const MOTION = {
  base: "200ms",
  ease: "cubic-bezier(0.2, 0.7, 0.2, 1)",
  fast: "120ms",
  slow: "320ms",
} as const;

/** The package registers the variable font under this name. The rest is the fallback stack. */
export const FONT_FAMILY = '"Geologica Variable", system-ui, -apple-system, "Segoe UI", sans-serif';

/** Sizes are in pixels. The theme turns them into rem, so they follow the browser's font size. */
export const TYPE_SCALE = {
  body: { fontSize: 15, fontWeight: 400, lineHeight: 1.4 },
  caption: { fontSize: 17, fontWeight: 400, lineHeight: 1.3 },
  "caption-small": { fontSize: 16, fontWeight: 400, lineHeight: 1.3 },
  hint: { fontSize: 14, fontWeight: 400, lineHeight: 1.35 },
  label: { fontSize: 17, fontWeight: 500, lineHeight: 1.3 },
  "sentence-cy": { fontSize: 30, fontWeight: 600, lineHeight: 1.25 },
  "sentence-en": { fontSize: 30, fontWeight: 400, lineHeight: 1.25 },
  title: { fontSize: 21, fontWeight: 600, lineHeight: 1.2 },
  wordmark: { fontSize: 18, fontWeight: 600, lineHeight: 1.2 },
} as const;

export const CARD_RADIUS = 10;
export const MINIMUM_TOUCH_TARGET = 48;

export const FOCUS_RING = { offset: 2, width: 3 } as const;
