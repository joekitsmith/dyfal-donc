const WIDE_GAP = 8;
const MEDIUM_GAP = 6;
const NARROW_GAP = 4;

const WIDE_GAP_MAXIMUM_BEATS = 10;
const MEDIUM_GAP_MAXIMUM_BEATS = 14;

export function beatGap(count: number): number {
  if (count <= WIDE_GAP_MAXIMUM_BEATS) {
    return WIDE_GAP;
  }

  return count <= MEDIUM_GAP_MAXIMUM_BEATS ? MEDIUM_GAP : NARROW_GAP;
}
