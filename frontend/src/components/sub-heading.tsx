import type { ReactNode } from "react";

import Box from "@mui/material/Box";

import { textStyle } from "@/theme/text-style";

type SubHeadingProps = {
  readonly children: ReactNode;
  /** Pages that have a title use h2 here, and sections within a section h3, which sit a little closer. */
  readonly level: "h2" | "h3";
  /** A line under the heading that says what the section is. */
  readonly note?: string;
};

/** Names a section of a page. */
export function SubHeading({ children, level, note }: SubHeadingProps) {
  return (
    <>
      <Box
        component={level}
        sx={{
          ...textStyle("body"),
          color: "var(--dd-muted)",
          fontWeight: 500,
          m: `${level === "h2" ? 28 : 24}px 0 ${note === undefined ? 8 : 2}px`,
        }}
      >
        {children}
      </Box>
      {note === undefined ? null : <Box sx={{ ...textStyle("hint"), color: "var(--dd-muted)", mb: "8px" }}>{note}</Box>}
    </>
  );
}
