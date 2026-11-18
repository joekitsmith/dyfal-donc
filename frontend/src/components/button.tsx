"use client";

import type { MouseEvent, ReactNode } from "react";

import ButtonBase from "@mui/material/ButtonBase";
import Link from "next/link";

import { textStyle } from "@/theme/text-style";

type ButtonProps = {
  readonly children: ReactNode;
  /** Shorter, for inside a card. A ghost button is always this size. */
  readonly compact?: boolean;
  /** A ghost button with an outline, for where it would otherwise not read as a button. */
  readonly edge?: boolean;
  /** As wide as its content, at the full height. */
  readonly fit?: boolean;
  readonly href?: string;
  readonly onClick?: () => void;
  readonly type?: "button" | "submit";
  /** Stays focusable but does nothing, so a button can wait for a request without disappearing. */
  readonly unavailable?: boolean;
  readonly variant: ButtonVariant;
};

type ButtonVariant = "ghost" | "primary" | "quiet";

const STANDALONE_HEIGHT = 56;
const COMPACT_HEIGHT = 48;

const VARIANT_STYLES = {
  ghost: {
    backgroundColor: "transparent",
    color: "var(--dd-ink)",
  },
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

const UNAVAILABLE_STYLES = {
  ghost: { color: "var(--dd-muted)" },
  primary: {
    backgroundColor: "transparent",
    border: "2px dashed var(--dd-line)",
    color: "var(--dd-muted)",
  },
  quiet: { color: "var(--dd-muted)" },
} as const;

export function Button({
  children,
  compact = false,
  edge = false,
  fit = false,
  href,
  onClick,
  type,
  unavailable = false,
  variant,
}: ButtonProps) {
  const small = compact || variant === "ghost";
  const sx = {
    ...textStyle("label"),
    ...(small ? { fontSize: "1rem" } : {}),
    ...VARIANT_STYLES[variant],
    ...(unavailable ? UNAVAILABLE_STYLES[variant] : {}),
    ...(edge ? { border: "2px solid var(--dd-line)" } : {}),
    "&:active": { transform: "scale(0.98)" },
    borderRadius: small ? "8px" : "10px",
    display: "flex",
    gap: "10px",
    height: small ? COMPACT_HEIGHT : STANDALONE_HEIGHT,
    justifyContent: "center",
    px: small ? "16px" : fit ? "22px" : "20px",
    transition: "transform var(--dd-fast) var(--dd-ease)",
    // A button does not fill its parent by itself, unlike a link
    width: small || fit ? "auto" : "100%",
  };

  // Cancelling the click also stops an unavailable submit button from sending its form
  const handleClick = (event: MouseEvent<HTMLElement>) => {
    if (unavailable) {
      event.preventDefault();

      return;
    }

    onClick?.();
  };

  if (href === undefined) {
    return (
      <ButtonBase aria-disabled={unavailable ? true : undefined} onClick={handleClick} sx={sx} type={type}>
        {children}
      </ButtonBase>
    );
  }

  return (
    <ButtonBase href={href} LinkComponent={Link} onClick={handleClick} sx={sx}>
      {children}
    </ButtonBase>
  );
}
