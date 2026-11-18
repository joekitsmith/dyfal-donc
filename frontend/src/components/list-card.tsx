import type { ReactNode } from "react";

import Box from "@mui/material/Box";

type ListCardProps = { readonly children: ReactNode };

/** Rows on one card, divided by lines. */
export function ListCard({ children }: ListCardProps) {
  return (
    <Box
      component="ul"
      sx={{ backgroundColor: "var(--dd-surface)", borderRadius: "10px", listStyle: "none", m: 0, p: "0 16px" }}
    >
      {children}
    </Box>
  );
}
