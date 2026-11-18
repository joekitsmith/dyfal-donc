import { countWords } from "./count-words";

const BASE_SECONDS = 2.16;
const SECONDS_PER_WORD = 0.72;
const MAXIMUM_SECONDS = 21.6;

/** How long the learner has to say the Welsh: a base plus time for each word, scaled by their setting. */
export function thinkSeconds(welsh: string, multiplier: number): number {
  const words = countWords(welsh);

  return Math.min(MAXIMUM_SECONDS, (BASE_SECONDS + SECONDS_PER_WORD * words) * multiplier);
}
