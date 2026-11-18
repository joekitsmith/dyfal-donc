import type { ReactNode } from "react";

import Box from "@mui/material/Box";

import { textStyle } from "@/theme/text-style";

type SubHeadingProps = {
  readonly children: ReactNode;
  /** Pages that have a title use h2 here, and sections within a section h3. */
  readonly level: "h2" | "h3";
};

/** Names a section of a page. */
export function SubHeading({ children, level }: SubHeadingProps) {
  return (
    <Box component={level} sx={{ ...textStyle("body"), color: "var(--dd-muted)", fontWeight: 500, m: "28px 0 8px" }}>
      {children}
    </Box>
  );
}
