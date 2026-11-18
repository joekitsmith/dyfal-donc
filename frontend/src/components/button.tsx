"use client";

import type { ReactNode } from "react";

import ButtonBase from "@mui/material/ButtonBase";
import Link from "next/link";

import { textStyle } from "@/theme/text-style";

type ButtonProps = {
  readonly children: ReactNode;
  readonly href?: string;
  readonly onClick?: () => void;
  readonly variant: ButtonVariant;
};

type ButtonVariant = "primary" | "quiet";

const BUTTON_HEIGHT = 56;

const VARIANT_STYLES = {
  primary: {
    backgroundColor: "var(--dd-inverse-bg)",
    color: "var(--dd-inverse-fg)",
    fontWeight: 600,
  },
  quiet: {
    backgroundColor: "var(--dd-surface)",
    color: "var(--dd-ink)",
  },
} as const;

export function Button({ children, href, onClick, variant }: ButtonProps) {
  const sx = {
    ...textStyle("label"),
    ...VARIANT_STYLES[variant],
    "&:active": { transform: "scale(0.98)" },
    borderRadius: "10px",
    height: BUTTON_HEIGHT,
    justifyContent: "center",
    px: "20px",
    transition: "transform var(--dd-fast) var(--dd-ease)",
  };

  if (href === undefined) {
    return (
      <ButtonBase onClick={onClick} sx={sx}>
        {children}
      </ButtonBase>
    );
  }

  return (
    <ButtonBase href={href} LinkComponent={Link} onClick={onClick} sx={sx}>
      {children}
    </ButtonBase>
  );
}
