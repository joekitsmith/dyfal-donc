import Box from "@mui/material/Box";
import ButtonBase from "@mui/material/ButtonBase";
import NextLink from "next/link";

import { textStyle } from "@/theme/text-style";

import { SlottedText } from "./slotted-text";

type ListRowProps = {
  /** Shown at the right. */
  readonly english?: string;
  readonly href: string;
  /** A second line under the Welsh, which makes the row taller. */
  readonly secondLine?: { readonly size: "body" | "small"; readonly text: string };
  readonly welsh: string;
};

const SECOND_LINE_STYLES = {
  body: textStyle("body"),
  small: { fontSize: "0.8125rem", fontWeight: 400, lineHeight: 1.35 },
} as const;

const ROW_HEIGHT = 52;
const TWO_LINE_ROW_HEIGHT = 64;

/** One row of a list card. The whole row is the link. */
export function ListRow({ english, href, secondLine, welsh }: ListRowProps) {
  return (
    <li>
      <ButtonBase
        href={href}
        LinkComponent={NextLink}
        sx={{
          alignItems: "center",
          display: "flex",
          gap: "12px",
          justifyContent: "space-between",
          minHeight: secondLine === undefined ? ROW_HEIGHT : TWO_LINE_ROW_HEIGHT,
          py: "10px",
          textAlign: "left",
          width: "100%",
        }}
      >
        <Box sx={{ display: "flex", flexDirection: "column", gap: "2px" }}>
          <Box lang="cy" sx={{ ...textStyle("label"), fontWeight: 600 }}>
            <SlottedText text={welsh} />
          </Box>
          {secondLine === undefined ? null : (
            <Box sx={{ ...SECOND_LINE_STYLES[secondLine.size], color: "var(--dd-muted)" }}>
              <SlottedText text={secondLine.text} />
            </Box>
          )}
        </Box>
        {english === undefined ? null : (
          <Box sx={{ ...textStyle("body"), color: "var(--dd-muted)", textAlign: "right" }}>
            <SlottedText text={english} />
          </Box>
        )}
      </ButtonBase>
    </li>
  );
}
