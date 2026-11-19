"use client";

import type { ReactNode } from "react";

import Box from "@mui/material/Box";
import Drawer from "@mui/material/Drawer";
import Popover from "@mui/material/Popover";
import { useTheme } from "@mui/material/styles";
import useMediaQuery from "@mui/material/useMediaQuery";

import { usePrefersReducedMotion } from "@/hooks/use-prefers-reduced-motion";
import { MOTION, SLOW_MILLISECONDS } from "@/theme/tokens";

type SheetProps = {
  /** Where the popover form attaches on a wide screen. Without it the sheet slides up even there. */
  readonly anchor: HTMLElement | null;
  readonly children: ReactNode;
  /** The name of the dialog, for a screen reader. */
  readonly label: string;
  readonly onClose: () => void;
  readonly open: boolean;
};

const POPOVER_WIDTH = 320;

// The lesson's shortcuts stand aside while something with this role is open
const DIALOG_ATTRIBUTES = { "aria-modal": true, role: "dialog" } as const;

export function Sheet({ anchor, children, label, onClose, open }: SheetProps) {
  const theme = useTheme();
  const reducedMotion = usePrefersReducedMotion();
  const wide = useMediaQuery(theme.breakpoints.up("md"), { noSsr: true });

  if (wide && anchor !== null) {
    return (
      <Popover
        anchorEl={anchor}
        anchorOrigin={{ horizontal: "right", vertical: "bottom" }}
        onClose={onClose}
        open={open}
        slotProps={{
          paper: {
            ...DIALOG_ATTRIBUTES,
            "aria-label": label,
            sx: {
              backgroundColor: "var(--dd-surface)",
              borderRadius: "10px",
              p: "10px 24px 20px",
              width: POPOVER_WIDTH,
            },
          },
        }}
        transformOrigin={{ horizontal: "right", vertical: "top" }}
      >
        {children}
      </Popover>
    );
  }

  return (
    <Drawer
      anchor="bottom"
      onClose={onClose}
      open={open}
      slotProps={{
        backdrop: { sx: { backgroundColor: "var(--dd-scrim)" } },
        paper: {
          ...DIALOG_ATTRIBUTES,
          "aria-label": label,
          sx: {
            backgroundColor: "var(--dd-surface)",
            borderRadius: "16px 16px 0 0",
            p: "10px 24px max(28px, env(safe-area-inset-bottom))",
          },
        },
        transition: { easing: MOTION.ease },
      }}
      transitionDuration={reducedMotion ? 0 : SLOW_MILLISECONDS}
    >
      <Box
        sx={{ backgroundColor: "var(--dd-line)", borderRadius: "2px", height: 4, mb: "8px", mx: "auto", width: 40 }}
      />
      {children}
    </Drawer>
  );
}
