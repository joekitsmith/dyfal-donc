import { createTheme } from "@mui/material/styles";

const MINIMUM_TOUCH_TARGET = 48;

export const theme = createTheme({
  colorSchemes: { dark: true, light: true },
  components: {
    MuiButton: {
      styleOverrides: { root: { minHeight: MINIMUM_TOUCH_TARGET, textTransform: "none" } },
    },
    MuiIconButton: {
      styleOverrides: { root: { minHeight: MINIMUM_TOUCH_TARGET, minWidth: MINIMUM_TOUCH_TARGET } },
    },
  },
  cssVariables: { colorSchemeSelector: "media" },
});
