import type { ReactNode } from "react";

import Box from "@mui/material/Box";

import { textStyle } from "@/theme/text-style";

type NoticeCardProps = {
  readonly children: ReactNode;
  /** Use "status" for a notice that appears after the page has loaded, so a screen reader announces it. */
  readonly role?: "status";
};

export function NoticeCard({ children, role }: NoticeCardProps) {
  return (
    <Box
      role={role}
      sx={{ ...textStyle("body"), backgroundColor: "var(--dd-surface)", borderRadius: "10px", p: "14px 16px" }}
    >
      {children}
    </Box>
  );
}
