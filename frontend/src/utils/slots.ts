export type SlotSegment =
  { readonly kind: "slot"; readonly name: string } | { readonly kind: "text"; readonly text: string };

const SLOT = /\[([A-Z]+)\]/g;

/**
 * Splits a pattern into its text and the slots in it, as in "Dw i'n moyn [VERB]". The text can run
 * on straight after a slot, as in "I like [VERB]ing", so the segments keep the text exactly as it is.
 */
export function parseSlots(template: string): readonly SlotSegment[] {
  const segments: SlotSegment[] = [];
  let from = 0;

  for (const match of template.matchAll(SLOT)) {
    if (match.index > from) {
      segments.push({ kind: "text", text: template.slice(from, match.index) });
    }

    segments.push({ kind: "slot", name: (match[1] ?? "").toLowerCase() });
    from = match.index + match[0].length;
  }

  if (from < template.length) {
    segments.push({ kind: "text", text: template.slice(from) });
  }

  return segments;
}
