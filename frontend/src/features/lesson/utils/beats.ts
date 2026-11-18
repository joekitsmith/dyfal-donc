import { countWords } from "./count-words";

/** The blocks that show the time to speak: one for each word, and three more. */
const EXTRA_BEATS = 3;

export function beatCount(welsh: string): number {
  return countWords(welsh) + EXTRA_BEATS;
}
