import { THINK_BASE_SECONDS, THINK_MAXIMUM_SECONDS, THINK_SECONDS_PER_WORD } from "../constants";

/** How long the learner has to say the Welsh: a base plus time for each word, scaled by their setting. */
export function thinkSeconds(welsh: string, multiplier: number): number {
  const words = welsh.split(/\s+/).filter((word) => word !== "").length;

  return Math.min(THINK_MAXIMUM_SECONDS, (THINK_BASE_SECONDS + THINK_SECONDS_PER_WORD * words) * multiplier);
}
