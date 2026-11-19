import type { ReactNode } from "react";

import Box from "@mui/material/Box";

type PageColumnProps = {
  readonly children: ReactNode;
  /** Fills the height of the window, so that something at the end of the content can sit at the bottom. */
  readonly fill?: boolean;
};

const COLUMN_WIDTH = 440;

/** The column of every screen that scrolls with its content, which is every screen except the ones in the lesson's frame. */
export function PageColumn({ children, fill = false }: PageColumnProps) {
  return (
    <Box
      component="main"
      sx={{
        ...(fill ? { boxSizing: "border-box", display: "flex", flexDirection: "column", minHeight: "100dvh" } : {}),
        maxWidth: COLUMN_WIDTH,
        mx: "auto",
        pb: "max(28px, calc(env(safe-area-inset-bottom) + 12px))",
        pt: "calc(20px + env(safe-area-inset-top))",
        px: "24px",
      }}
    >
      {children}
    </Box>
  );
}
