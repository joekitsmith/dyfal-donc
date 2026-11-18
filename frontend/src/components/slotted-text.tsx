import { parseSlots } from "@/utils/slots";

import { SlotChip } from "./slot-chip";

type SlottedTextProps = {
  /** For text in a heading. */
  readonly chip?: "heading" | "text";
  readonly text: string;
};

/** Text in which each slot, like [VERB], is drawn as a chip. */
export function SlottedText({ chip = "text", text }: SlottedTextProps) {
  return parseSlots(text).map((segment, index) =>
    segment.kind === "slot" ? <SlotChip key={index} name={segment.name} size={chip} /> : segment.text,
  );
}
