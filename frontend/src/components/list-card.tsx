import type { ReactNode } from "react";

import Box from "@mui/material/Box";

type ListCardProps = {
  readonly children: ReactNode;
  /** The name of the list, for a screen reader. */
  readonly label?: string;
};

/** Rows on one card, divided by lines. */
export function ListCard({ children, label }: ListCardProps) {
  return (
    <Box
      aria-label={label}
      component="ul"
      sx={{
        "& > li": { "&:last-child": { borderBottom: 0 }, borderBottom: "1px solid var(--dd-divider)" },
        backgroundColor: "var(--dd-surface)",
        borderRadius: "10px",
        listStyle: "none",
        m: 0,
        p: "0 16px",
      }}
    >
      {children}
    </Box>
  );
}
