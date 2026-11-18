import Box from "@mui/material/Box";
import ButtonBase from "@mui/material/ButtonBase";
import NextLink from "next/link";

import { textStyle } from "@/theme/text-style";

import { ChevronIcon } from "./icons/chevron-icon";

type PageHeaderProps = {
  readonly back: { readonly href: string };
  readonly title: string;
};

const HEADER_HEIGHT = 48;

export function PageHeader({ back, title }: PageHeaderProps) {
  return (
    // Shifted left so that the icon, not the whole tap target, lines up with the column
    <Box sx={{ alignItems: "center", display: "flex", gap: "4px", height: HEADER_HEIGHT, ml: "-12px" }}>
      <ButtonBase
        aria-label="Back"
        href={back.href}
        LinkComponent={NextLink}
        sx={{ height: HEADER_HEIGHT, justifyContent: "center", width: HEADER_HEIGHT }}
      >
        <ChevronIcon direction="left" size={24} />
      </ButtonBase>
      <Box component="h1" sx={{ ...textStyle("title"), m: 0 }}>
        {title}
      </Box>
    </Box>
  );
}
