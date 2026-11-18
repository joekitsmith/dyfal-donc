import type { ReactNode } from "react";

import Box from "@mui/material/Box";

import { textStyle } from "@/theme/text-style";

import { AppMark } from "./app-mark";

type AppHeaderProps = {
  readonly clock?: ReactNode;
  readonly menu?: ReactNode;
};

const HEADER_HEIGHT = 44;

export function AppHeader({ clock, menu }: AppHeaderProps) {
  return (
    <Box
      component="header"
      sx={{
        alignItems: "center",
        display: "flex",
        flexShrink: 0,
        height: HEADER_HEIGHT,
        justifyContent: "space-between",
        mt: "calc(20px + env(safe-area-inset-top))",
      }}
    >
      <Box sx={{ alignItems: "center", display: "flex", gap: "10px" }}>
        <AppMark />
        <Box component="span" sx={textStyle("wordmark")}>
          dyfal-donc
        </Box>
      </Box>
      <Box sx={{ alignItems: "center", display: "flex", gap: "8px" }}>
        {clock}
        {/* Shifted right so that the dots, not the whole tap target, line up with the column */}
        {menu === undefined ? null : <Box sx={{ mr: "-12px" }}>{menu}</Box>}
      </Box>
    </Box>
  );
}
