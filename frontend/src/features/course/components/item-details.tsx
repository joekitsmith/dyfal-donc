import Box from "@mui/material/Box";

import { Button } from "@/components/button";
import { PlayIcon } from "@/components/icons/play-icon";
import { SlottedText } from "@/components/slotted-text";
import { textStyle } from "@/theme/text-style";
import { parseSlots } from "@/utils/slots";

import type { ItemDetail } from "../types";

import { formatFirstMet } from "../utils/format-first-met";

type ItemDetailsProps = {
  readonly item: ItemDetail;
  readonly playback: {
    readonly failed: boolean;
    /** Without it the item has nothing to hear, as a phrase has not. */
    readonly play: (() => void) | undefined;
  };
};

/** An item in both languages, how to hear it if it is a word, and what else is known about it. */
export function ItemDetails({ item, playback }: ItemDetailsProps) {
  const hasSlot = parseSlots(item.welsh).some((segment) => segment.kind === "slot");

  return (
    <>
      <Box sx={{ ...textStyle("body"), color: "var(--dd-muted)", mt: "28px" }}>
        {item.kind === "word" ? "Word" : "Way of saying things"}
      </Box>
      <Box component="h1" lang="cy" sx={{ ...textStyle("sentence-cy"), lineHeight: 1.3, m: "4px 0 0" }}>
        <SlottedText chip="heading" text={item.welsh} />
      </Box>
      <Box sx={{ ...textStyle("title"), color: "var(--dd-muted)", fontWeight: 400, mt: "2px" }}>
        <SlottedText text={item.english} />
      </Box>
      {playback.play === undefined ? null : (
        <Box sx={{ mt: "20px" }}>
          <Box sx={{ display: "flex" }}>
            <Button fit onClick={playback.play} variant="quiet">
              <PlayIcon size={18} />
              Hear it
            </Button>
          </Box>
          {playback.failed ? (
            <Box role="status" sx={{ ...textStyle("hint"), color: "var(--dd-muted)", mt: "8px" }}>
              That couldn&apos;t be played. Try again.
            </Box>
          ) : null}
        </Box>
      )}
      <Box sx={{ ...textStyle("body"), display: "flex", flexDirection: "column", gap: "6px", mt: "24px" }}>
        {hasSlot ? <Box>The outlined part is where a word goes.</Box> : null}
        {item.forms.length === 0 ? null : (
          <Box>
            Other forms:{" "}
            <Box component="span" lang="cy" sx={{ fontWeight: 600 }}>
              {item.forms.join(", ")}
            </Box>
          </Box>
        )}
        {item.notes === "" ? null : <Box>{item.notes}</Box>}
        <Box sx={{ color: "var(--dd-muted)" }}>First met {formatFirstMet(item.first_met_at)}</Box>
      </Box>
    </>
  );
}
