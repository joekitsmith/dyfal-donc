import Box from "@mui/material/Box";

import { textStyle } from "@/theme/text-style";
import { MEDIA } from "@/theme/tokens";

type KeyHintProps = {
  readonly children: string;
  /** Beside the content of a button that is only as wide as that, or at the right-hand edge of one that is wider. */
  readonly inline?: boolean;
  /** On a dark button, where the muted colour would be too faint to read. */
  readonly onInverse?: boolean;
};

/** The key that presses a control. It is only there where there is a keyboard, and it is not read aloud, because the control's name says what it does. */
export function KeyHint({ children, inline = false, onInverse = false }: KeyHintProps) {
  return (
    <Box
      aria-hidden="true"
      component="span"
      sx={{
        ...textStyle("hint"),
        color: onInverse ? "inherit" : "var(--dd-muted)",
        display: "none",
        fontWeight: 400,
        ...(inline ? { ml: "12px" } : { position: "absolute", right: "16px" }),
        [MEDIA.keyboard]: { display: "inline" },
      }}
    >
      {children}
    </Box>
  );
}
