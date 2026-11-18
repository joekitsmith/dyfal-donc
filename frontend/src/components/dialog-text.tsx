import type { ReactNode } from "react";

import Box from "@mui/material/Box";

import { textStyle } from "@/theme/text-style";

type DialogTextProps = { readonly children: ReactNode };

/** The words under a dialog's title. */
export function DialogText({ children }: DialogTextProps) {
  return <Box sx={{ ...textStyle("body"), mt: "8px" }}>{children}</Box>;
}
