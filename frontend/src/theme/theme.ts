import type { Shadows } from "@mui/material/styles";

import { createTheme } from "@mui/material/styles";

import { CARD_RADIUS, COLOURS, FOCUS_RING, FONT_FAMILY, MINIMUM_TOUCH_TARGET, MOTION, TYPE_SCALE } from "./tokens";

const BASE_FONT_SIZE = 16;
const SHADOW_LEVELS = 25;

const NO_SHADOWS = Array.from({ length: SHADOW_LEVELS }, () => "none") as unknown as Shadows;

const FOCUS_RING_STYLE = {
  outline: `${FOCUS_RING.width}px solid var(--dd-accent)`,
  outlineOffset: `${FOCUS_RING.offset}px`,
} as const;

function customProperties(values: Readonly<Record<string, string>>) {
  return Object.fromEntries(Object.entries(values).map(([name, value]) => [`--dd-${name}`, value]));
}

function textStyle(style: { readonly fontSize: number; readonly fontWeight: number; readonly lineHeight: number }) {
  return { ...style, fontSize: `${style.fontSize / BASE_FONT_SIZE}rem` };
}

function scheme(colours: typeof COLOURS.dark | typeof COLOURS.light) {
  return {
    palette: {
      background: { default: colours.ground, paper: colours.surface },
      divider: colours.divider,
      // The design has no red. Everything that is not the accent is ink, so MUI's own alerts follow
      error: { contrastText: colours["inverse-fg"], main: colours.ink },
      info: { contrastText: colours["inverse-fg"], main: colours.ink },
      primary: { contrastText: colours["inverse-fg"], main: colours["inverse-bg"] },
      secondary: { contrastText: colours["inverse-fg"], main: colours.ink },
      success: { contrastText: colours["inverse-fg"], main: colours.accent },
      text: { disabled: colours.muted, primary: colours.ink, secondary: colours.muted },
      warning: { contrastText: colours["inverse-fg"], main: colours.ink },
    },
  };
}

export const theme = createTheme({
  colorSchemes: { dark: scheme(COLOURS.dark), light: scheme(COLOURS.light) },
  components: {
    MuiButton: {
      defaultProps: { disableElevation: true },
      styleOverrides: { root: { minHeight: MINIMUM_TOUCH_TARGET, textTransform: "none" } },
    },
    MuiButtonBase: {
      defaultProps: { disableRipple: true },
      styleOverrides: { root: { "&:focus-visible": FOCUS_RING_STYLE } },
    },
    MuiCssBaseline: {
      styleOverrides: {
        ":focus-visible": FOCUS_RING_STYLE,
        ":root": {
          ...customProperties(COLOURS.light),
          ...customProperties(MOTION),
          "@media (prefers-color-scheme: dark)": customProperties(COLOURS.dark),
          colorScheme: "light dark",
        },
        body: { fontVariantNumeric: "tabular-nums" },
      },
    },
    MuiIconButton: {
      styleOverrides: { root: { minHeight: MINIMUM_TOUCH_TARGET, minWidth: MINIMUM_TOUCH_TARGET } },
    },
    MuiPaper: {
      // Dark mode paints a lighter gradient over raised surfaces, and the design has no gradients
      styleOverrides: { root: { backgroundImage: "none" } },
    },
  },
  cssVariables: { colorSchemeSelector: "media" },
  shadows: NO_SHADOWS,
  shape: { borderRadius: CARD_RADIUS },
  typography: {
    body1: textStyle(TYPE_SCALE.body),
    body2: textStyle(TYPE_SCALE.body),
    button: { ...textStyle(TYPE_SCALE.label), textTransform: "none" },
    caption: textStyle(TYPE_SCALE.hint),
    fontFamily: FONT_FAMILY,
    fontWeightBold: 600,
    fontWeightMedium: 500,
    fontWeightRegular: 400,
    h1: textStyle(TYPE_SCALE.title),
    h2: textStyle(TYPE_SCALE.title),
    h3: textStyle(TYPE_SCALE.title),
    h4: textStyle(TYPE_SCALE.title),
    h5: textStyle(TYPE_SCALE.title),
    h6: textStyle(TYPE_SCALE.title),
    subtitle1: textStyle(TYPE_SCALE.label),
    subtitle2: textStyle(TYPE_SCALE.body),
  },
});
