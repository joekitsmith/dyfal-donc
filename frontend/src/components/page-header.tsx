import Box from "@mui/material/Box";
import ButtonBase from "@mui/material/ButtonBase";
import NextLink from "next/link";

import { textStyle } from "@/theme/text-style";

import { ChevronIcon } from "./icons/chevron-icon";

type PageHeaderProps = { readonly back: { readonly href: string } } & (
  { readonly backLabel: string; readonly title?: never } | { readonly backLabel?: never; readonly title: string }
);

const HEADER_HEIGHT = 48;

/**
 * The top of a page, with the way back. Most pages have a title beside the arrow. A page that is
 * itself the title, as a word's page is, has the name of where the arrow goes instead, as one link.
 */
export function PageHeader({ back, backLabel, title }: PageHeaderProps) {
  if (backLabel !== undefined) {
    return (
      <ButtonBase
        href={back.href}
        LinkComponent={NextLink}
        sx={{
          ...textStyle("body"),
          gap: "4px",
          height: HEADER_HEIGHT,
          justifyContent: "flex-start",
          // Shifted left so that the icon, not the whole tap target, lines up with the column
          ml: "-12px",
          pl: "12px",
          pr: "12px",
        }}
      >
        <ChevronIcon direction="left" size={24} />
        {backLabel}
      </ButtonBase>
    );
  }

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
