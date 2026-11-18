import type { ReactNode } from "react";

import Typography from "@mui/material/Typography";

type LeadTextProps = {
  readonly children: ReactNode;
  readonly muted?: boolean;
};

export function LeadText({ children, muted = false }: LeadTextProps) {
  return (
    <Typography sx={{ color: muted ? "var(--dd-muted)" : "var(--dd-ink)", fontSize: "1.0625rem", lineHeight: 1.45 }}>
      {children}
    </Typography>
  );
}
