import Box from "@mui/material/Box";
import ButtonBase from "@mui/material/ButtonBase";
import NextLink from "next/link";

import { textStyle } from "@/theme/text-style";

import { SlottedText } from "./slotted-text";

type ListRowProps = {
  readonly english: string;
  readonly href: string;
  readonly welsh: string;
};

const ROW_HEIGHT = 52;

/** One row of a list card. The whole row is the link. */
export function ListRow({ english, href, welsh }: ListRowProps) {
  return (
    <Box component="li" sx={{ "&:last-child": { borderBottom: 0 }, borderBottom: "1px solid var(--dd-divider)" }}>
      <ButtonBase
        href={href}
        LinkComponent={NextLink}
        sx={{
          alignItems: "center",
          display: "flex",
          gap: "12px",
          justifyContent: "space-between",
          minHeight: ROW_HEIGHT,
          py: "10px",
          textAlign: "left",
          width: "100%",
        }}
      >
        <Box lang="cy" sx={{ ...textStyle("label"), fontWeight: 600 }}>
          <SlottedText text={welsh} />
        </Box>
        <Box sx={{ ...textStyle("body"), color: "var(--dd-muted)", textAlign: "right" }}>
          <SlottedText text={english} />
        </Box>
      </ButtonBase>
    </Box>
  );
}
