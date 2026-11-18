import type { ReactNode } from "react";

import ButtonBase from "@mui/material/ButtonBase";

import { textStyle } from "@/theme/text-style";

type TextButtonProps = {
  readonly children: ReactNode;
  readonly onClick: () => void;
};

/** An action that is quiet enough to look like text, for what few will need. */
export function TextButton({ children, onClick }: TextButtonProps) {
  return (
    <ButtonBase
      onClick={onClick}
      sx={{
        ...textStyle("body"),
        color: "var(--dd-muted)",
        justifyContent: "flex-start",
        minHeight: 48,
        textDecoration: "underline",
      }}
    >
      {children}
    </ButtonBase>
  );
}
