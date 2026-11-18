import type { ReactNode } from "react";

import Box from "@mui/material/Box";

import { textStyle } from "@/theme/text-style";

import { TickIcon } from "./icons/tick-icon";

type NoticeCardProps = {
  /** Buttons under the text, the main one first. */
  readonly actions?: ReactNode;
  readonly children: ReactNode;
  /** Says that something has been done: it has a tick, and is announced as it appears. */
  readonly confirmation?: boolean;
  /** A line under the buttons, for what the button will do. */
  readonly hint?: string;
  /** Use "status" for a notice that appears after the page has loaded, so a screen reader announces it. */
  readonly role?: "status";
};

export function NoticeCard({ actions, children, confirmation = false, hint, role }: NoticeCardProps) {
  return (
    <Box
      role={confirmation ? "status" : role}
      sx={{
        ...textStyle("body"),
        backgroundColor: "var(--dd-surface)",
        borderRadius: "10px",
        p: "14px 16px",
        ...(confirmation ? { alignItems: "center", display: "flex", gap: "12px" } : {}),
      }}
    >
      {confirmation ? (
        <Box aria-hidden="true" sx={{ color: "var(--dd-accent)", display: "flex", flexShrink: 0 }}>
          <TickIcon size={22} />
        </Box>
      ) : null}
      {children}
      {actions === undefined ? null : (
        <Box sx={{ display: "flex", flexWrap: "wrap", gap: "8px", mt: "10px" }}>{actions}</Box>
      )}
      {hint === undefined ? null : <Box sx={{ ...textStyle("hint"), color: "var(--dd-muted)", mt: "8px" }}>{hint}</Box>}
    </Box>
  );
}
