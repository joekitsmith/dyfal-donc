import type { ReactNode } from "react";

import ButtonBase from "@mui/material/ButtonBase";
import NextLink from "next/link";

import { ChevronIcon } from "@/components/icons/chevron-icon";
import { textStyle } from "@/theme/text-style";

type MenuRowProps = {
  /** Shown at the right to say the row leads somewhere. */
  readonly chevron?: boolean;
  readonly children: ReactNode;
  /** Makes the row a link. */
  readonly href?: string;
  readonly onClick?: () => void;
};

const ROW_HEIGHT = 56;

export function MenuRow({ chevron = true, children, href, onClick }: MenuRowProps) {
  const sx = {
    ...textStyle("label"),
    borderBottom: "1px solid var(--dd-divider)",
    height: ROW_HEIGHT,
    justifyContent: "space-between",
    textAlign: "left",
    width: "100%",
  } as const;
  const content = (
    <>
      {children}
      {chevron ? <ChevronIcon direction="right" size={18} /> : null}
    </>
  );

  if (href === undefined) {
    return (
      <ButtonBase onClick={onClick} sx={sx}>
        {content}
      </ButtonBase>
    );
  }

  return (
    <ButtonBase href={href} LinkComponent={NextLink} sx={sx}>
      {content}
    </ButtonBase>
  );
}
