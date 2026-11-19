import type { Shadows } from "@mui/material/styles";

import { createTheme } from "@mui/material/styles";

import { textStyle } from "./text-style";
import { CARD_RADIUS, COLOURS, FOCUS_RING, FONT_FAMILY, MEDIA, MINIMUM_TOUCH_TARGET, MOTION } from "./tokens";

const SHADOW_LEVELS = 25;

const NO_SHADOWS = Array.from({ length: SHADOW_LEVELS }, () => "none") as unknown as Shadows;

const FOCUS_RING_STYLE = {
  outline: `${FOCUS_RING.width}px solid var(--dd-accent)`,
  outlineOffset: `${FOCUS_RING.offset}px`,
} as const;

function customProperties(values: Readonly<Record<string, string>>) {
  return Object.fromEntries(Object.entries(values).map(([name, value]) => [`--dd-${name}`, value]));
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
          // Fades stay, quicker. Whatever moves is instant, so nothing slides or opens along a seam
          [MEDIA.reducedMotion]: { "--dd-base": MOTION.fast, "--dd-slow": "0ms" },
        },
        body: { fontVariantNumeric: "tabular-nums" },
        // Form controls ignore the page font unless told to inherit it
        "button, input, select, textarea": { fontFamily: "inherit" },
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
    body1: textStyle("body"),
    body2: textStyle("body"),
    button: { ...textStyle("label"), textTransform: "none" },
    caption: textStyle("hint"),
    fontFamily: FONT_FAMILY,
    fontWeightBold: 600,
    fontWeightMedium: 500,
    fontWeightRegular: 400,
    h1: textStyle("title"),
    h2: textStyle("title"),
    h3: textStyle("title"),
    h4: textStyle("title"),
    h5: textStyle("title"),
    h6: textStyle("title"),
    subtitle1: textStyle("label"),
    subtitle2: textStyle("body"),
  },
});
