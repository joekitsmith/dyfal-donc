"use client";

import type { MouseEvent, ReactNode } from "react";

import ButtonBase from "@mui/material/ButtonBase";
import Link from "next/link";

import { textStyle } from "@/theme/text-style";

type ButtonProps = {
  readonly children: ReactNode;
  readonly href?: string;
  readonly onClick?: () => void;
  readonly type?: "button" | "submit";
  /** Stays focusable but does nothing, so a button can wait for a request without disappearing. */
  readonly unavailable?: boolean;
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

const UNAVAILABLE_STYLES = {
  primary: {
    backgroundColor: "transparent",
    border: "2px dashed var(--dd-line)",
    color: "var(--dd-muted)",
  },
  quiet: { color: "var(--dd-muted)" },
} as const;

export function Button({ children, href, onClick, type, unavailable = false, variant }: ButtonProps) {
  const sx = {
    ...textStyle("label"),
    ...VARIANT_STYLES[variant],
    ...(unavailable ? UNAVAILABLE_STYLES[variant] : {}),
    "&:active": { transform: "scale(0.98)" },
    borderRadius: "10px",
    display: "flex",
    height: BUTTON_HEIGHT,
    justifyContent: "center",
    px: "20px",
    transition: "transform var(--dd-fast) var(--dd-ease)",
    width: "100%",
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
