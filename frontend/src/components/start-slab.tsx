"use client";

import type { ReactNode } from "react";

import Box from "@mui/material/Box";
import ButtonBase from "@mui/material/ButtonBase";

import { textStyle } from "@/theme/text-style";
import { HOVER_OUTLINE, MEDIA } from "@/theme/tokens";

import { PlayIcon } from "./icons/play-icon";
import { KeyHint } from "./key-hint";

type StartSlabProps = {
  /** The key that presses it, shown where there is a keyboard. */
  readonly keyHint?: string;
  readonly onClick: () => void;
  readonly subtitle: ReactNode;
  readonly title: ReactNode;
  /** Stays focusable but does nothing, so the slab can wait for a request without disappearing. */
  readonly unavailable?: boolean;
};

const SLAB_HEIGHT = 88;

const AVAILABLE_STYLE = { backgroundColor: "var(--dd-inverse-bg)", color: "var(--dd-inverse-fg)" } as const;

const UNAVAILABLE_STYLE = {
  backgroundColor: "transparent",
  border: "2px dashed var(--dd-line)",
  color: "var(--dd-muted)",
} as const;

export function StartSlab({ keyHint, onClick, subtitle, title, unavailable = false }: StartSlabProps) {
  return (
    <ButtonBase
      aria-disabled={unavailable ? true : undefined}
      onClick={unavailable ? undefined : onClick}
      sx={{
        ...(unavailable ? UNAVAILABLE_STYLE : AVAILABLE_STYLE),
        "&:active": { [MEDIA.reducedMotion]: { transform: "none" }, transform: "scale(0.98)" },
        borderRadius: "10px",
        flexShrink: 0,
        gap: "16px",
        height: SLAB_HEIGHT,
        justifyContent: "center",
        [MEDIA.hover]: { "&:hover": HOVER_OUTLINE },
        transition: "transform var(--dd-fast) var(--dd-ease)",
        width: "100%",
      }}
    >
      <PlayIcon size={30} />
      <Box component="span" sx={{ alignItems: "flex-start", display: "flex", flexDirection: "column" }}>
        <Box component="span" sx={{ fontSize: "1.5rem", fontWeight: 600, lineHeight: 1.15 }}>
          {title}
        </Box>
        <Box component="span" sx={textStyle("body")}>
          {subtitle}
        </Box>
      </Box>
      {keyHint === undefined ? null : <KeyHint onInverse={!unavailable}>{keyHint}</KeyHint>}
    </ButtonBase>
  );
}
