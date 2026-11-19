"use client";

import type { ReactNode } from "react";

import Box from "@mui/material/Box";
import ButtonBase from "@mui/material/ButtonBase";
import MuiDialog from "@mui/material/Dialog";
import { useId } from "react";

import { textStyle } from "@/theme/text-style";

import { CloseIcon } from "./icons/close-icon";

type DialogProps = {
  readonly children: ReactNode;
  /** A close button beside the title. It needs `onClose`. */
  readonly closeButton?: boolean;
  /** On a phone, fills the screen instead of rising from the bottom, for a dialog with a form in it. */
  readonly fillsPhone?: boolean;
  /** Called when Escape or a tap outside closes it. Without it the dialog can only be answered. */
  readonly onClose?: () => void;
  readonly open: boolean;
  readonly title: string;
};

const WIDE_WIDTH = 480;
const CLOSE_SIZE = 48;

/** Rises from the bottom of a phone, and is centred on a wide screen. */
export function Dialog({ children, closeButton = false, fillsPhone = false, onClose, open, title }: DialogProps) {
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
            borderRadius: { md: "10px", xs: fillsPhone ? 0 : "16px 16px 0 0" },
            display: "flex",
            flexDirection: "column",
            height: { md: "auto", xs: fillsPhone ? "100dvh" : "auto" },
            m: 0,
            maxHeight: { md: "calc(100% - 64px)", xs: "none" },
            maxWidth: { md: WIDE_WIDTH, xs: "none" },
            p: {
              md: "24px",
              xs: fillsPhone
                ? "max(24px, env(safe-area-inset-top)) 24px max(24px, env(safe-area-inset-bottom))"
                : "24px 24px max(28px, env(safe-area-inset-bottom))",
            },
            width: "100%",
          },
        },
      }}
      sx={{ "& .MuiDialog-container": { alignItems: { md: "center", xs: "flex-end" } } }}
    >
      <Box sx={{ alignItems: "center", display: "flex", justifyContent: "space-between" }}>
        <Box component="h2" id={titleId} sx={{ ...textStyle("title"), m: 0 }}>
          {title}
        </Box>
        {closeButton ? (
          <ButtonBase
            aria-label="Close"
            onClick={onClose}
            // Shifted right so that the icon, not the whole tap target, lines up with the edge
            sx={{ height: CLOSE_SIZE, mr: "-12px", width: CLOSE_SIZE }}
          >
            <CloseIcon size={24} />
          </ButtonBase>
        ) : null}
      </Box>
      {children}
    </MuiDialog>
  );
}
