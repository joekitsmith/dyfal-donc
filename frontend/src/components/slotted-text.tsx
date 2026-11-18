import { parseSlots } from "@/utils/slots";

import { SlotChip } from "./slot-chip";

type SlottedTextProps = { readonly text: string };

/** Text in which each slot, like [VERB], is drawn as a chip. */
export function SlottedText({ text }: SlottedTextProps) {
  return parseSlots(text).map((segment, index) =>
    segment.kind === "slot" ? <SlotChip key={index} name={segment.name} /> : segment.text,
  );
}
