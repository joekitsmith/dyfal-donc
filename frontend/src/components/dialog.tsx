"use client";

import type { ReactNode } from "react";

import Box from "@mui/material/Box";
import MuiDialog from "@mui/material/Dialog";
import { useId } from "react";

import { textStyle } from "@/theme/text-style";

type DialogProps = {
  readonly children: ReactNode;
  /** Called when Escape or a tap outside closes it. Without it the dialog can only be answered. */
  readonly onClose?: () => void;
  readonly open: boolean;
  readonly title: string;
};

const WIDE_WIDTH = 480;

/** Rises from the bottom of a phone, and is centred on a wide screen. */
export function Dialog({ children, onClose, open, title }: DialogProps) {
  const titleId = useId();

  return (
    <MuiDialog
      aria-labelledby={titleId}
      onClose={onClose}
      open={open}
      slotProps={{
        backdrop: { sx: { backgroundColor: "var(--dd-scrim)" } },
        paper: {
          sx: {
            backgroundColor: "var(--dd-surface)",
            backgroundImage: "none",
            borderRadius: { md: "10px", xs: "16px 16px 0 0" },
            m: 0,
            maxWidth: { md: WIDE_WIDTH, xs: "none" },
            p: "24px 24px max(28px, env(safe-area-inset-bottom))",
            width: "100%",
          },
        },
      }}
      sx={{ "& .MuiDialog-container": { alignItems: { md: "center", xs: "flex-end" } } }}
    >
      <Box component="h2" id={titleId} sx={{ ...textStyle("title"), m: 0 }}>
        {title}
      </Box>
      {children}
    </MuiDialog>
  );
}
