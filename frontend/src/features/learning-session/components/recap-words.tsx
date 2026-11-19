import Box from "@mui/material/Box";
import NextLink from "next/link";
import { Fragment } from "react";

import { courseItemPath, learningSessionPath } from "@/config/paths";
import { textStyle } from "@/theme/text-style";

import type { Item } from "../types";

import { shortenSlots } from "../utils/shorten-slots";

type RecapWordsProps = {
  readonly items: readonly Item[];
  readonly sessionId: number;
};

const MAXIMUM_SHOWN = 6;

/** The padding makes the link as tall to press as any other. On a line of text it takes no room. */
const LINK_STYLE = { color: "inherit", paddingBlock: "11px", textDecoration: "underline" } as const;

/** The new words met in a session, each a link to its page, or a plain line when everything was practice. */
export function RecapWords({ items, sessionId }: RecapWordsProps) {
  if (items.length === 0) {
    return <Box sx={{ ...textStyle("caption"), mt: "6px" }}>Nothing new, all practice.</Box>;
  }

  const hidden = items.length - MAXIMUM_SHOWN;

  return (
    <Box sx={{ fontSize: "1.375rem", fontWeight: 600, lineHeight: 1.3, mt: "6px" }}>
      {items.slice(0, MAXIMUM_SHOWN).map((item, index) => (
        <Fragment key={item.id}>
          {index === 0 ? null : ", "}
          <NextLink href={courseItemPath(item.id)} lang="cy" style={LINK_STYLE}>
            {shortenSlots(item.welsh)}
          </NextLink>
        </Fragment>
      ))}
      {hidden > 0 ? (
        <>
          {" "}
          <NextLink href={learningSessionPath(sessionId)} style={LINK_STYLE}>
            and {hidden} more
          </NextLink>
        </>
      ) : null}
    </Box>
  );
}
