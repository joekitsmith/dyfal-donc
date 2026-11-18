import Box from "@mui/material/Box";

import { textStyle } from "@/theme/text-style";

import { AppMark } from "./app-mark";

const HEADER_HEIGHT = 44;

export function AppHeader() {
  return (
    <Box
      component="header"
      sx={{
        alignItems: "center",
        display: "flex",
        flexShrink: 0,
        gap: "10px",
        height: HEADER_HEIGHT,
        mt: "calc(20px + env(safe-area-inset-top))",
      }}
    >
      <AppMark />
      <Box component="span" sx={textStyle("wordmark")}>
        dyfal-donc
      </Box>
    </Box>
  );
}
