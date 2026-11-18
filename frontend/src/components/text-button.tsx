import type { ReactNode } from "react";

import ButtonBase from "@mui/material/ButtonBase";

import { textStyle } from "@/theme/text-style";

type TextButtonProps = {
  /** Sits in the middle of its line instead of at the start. */
  readonly centred?: boolean;
  readonly children: ReactNode;
  readonly onClick: () => void;
};

/** An action that is quiet enough to look like text, for what few will need. */
export function TextButton({ centred = false, children, onClick }: TextButtonProps) {
  return (
    <ButtonBase
      onClick={onClick}
      sx={{
        ...textStyle("body"),
        color: "var(--dd-muted)",
        justifyContent: centred ? "center" : "flex-start",
        ...(centred ? { display: "flex", width: "100%" } : {}),
        minHeight: 48,
        textDecoration: "underline",
      }}
    >
      {children}
    </ButtonBase>
  );
}
