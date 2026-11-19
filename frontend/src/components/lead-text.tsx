import type { ReactNode } from "react";

import Box from "@mui/material/Box";

type LeadTextProps = {
  readonly children: ReactNode;
  readonly muted?: boolean;
};

export function LeadText({ children, muted = false }: LeadTextProps) {
  return (
    <Box
      component="p"
      sx={{ color: muted ? "var(--dd-muted)" : "var(--dd-ink)", fontSize: "1.0625rem", lineHeight: 1.45, m: 0 }}
    >
      {children}
    </Box>
  );
}
