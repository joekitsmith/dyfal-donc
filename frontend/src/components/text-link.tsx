import type { ReactNode } from "react";

import ButtonBase from "@mui/material/ButtonBase";
import NextLink from "next/link";

type TextLinkProps = {
  readonly children: ReactNode;
  readonly href: string;
  /** Stays focusable but goes nowhere, for while another request is under way. */
  readonly unavailable?: boolean;
};

export function TextLink({ children, href, unavailable = false }: TextLinkProps) {
  return (
    <ButtonBase
      aria-disabled={unavailable ? true : undefined}
      href={href}
      LinkComponent={NextLink}
      onClick={(event) => {
        if (unavailable) {
          event.preventDefault();
        }
      }}
      sx={{
        color: unavailable ? "var(--dd-muted)" : "var(--dd-ink)",
        fontSize: "1rem",
        justifyContent: "center",
        minHeight: 48,
        textDecoration: "underline",
      }}
    >
      {children}
    </ButtonBase>
  );
}
