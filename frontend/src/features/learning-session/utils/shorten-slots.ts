/** A pattern with the word that goes in its slot left out, as "Dw i'n moyn…", for where it is listed among words. */
export function shortenSlots(welsh: string): string {
  return welsh.replaceAll(/ ?\[[^\]]+\]/g, "…");
}
