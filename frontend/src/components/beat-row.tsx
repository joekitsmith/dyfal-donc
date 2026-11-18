"use client";

import Box from "@mui/material/Box";
import { keyframes } from "@mui/material/styles";

import { TEST_IDS } from "@/config/test-ids";
import { beatGap } from "@/utils/beat-gap";

type BeatRowProps = {
  readonly count: number;
  /** Blocks before it are done and blocks after it are to come. Without it, all are to come. */
  readonly nowIndex?: number;
  /** Each block splits along a seam, which is how the row shows that the Welsh has been said. */
  readonly opened?: boolean;
  /** The block that is now pulses, to show that something is being waited for. */
  readonly waiting?: boolean;
};

type BeatState = "done" | "now" | "to-come";

const ROW_HEIGHT = 48;
const HALF_HEIGHT = 20;
const SEAM_OFFSET = 4;

const BLOCK_STYLES = {
  done: { backgroundColor: "var(--dd-ink)", borderColor: "var(--dd-ink)" },
  now: { backgroundColor: "var(--dd-accent)", borderColor: "var(--dd-accent)" },
  "to-come": { backgroundColor: "transparent", borderColor: "var(--dd-line)" },
} as const;

const pulse = keyframes({ "50%": { opacity: 0.4 } });

const OPENING = "var(--dd-slow) var(--dd-ease)";

/** The time the learner has to speak, drawn as blocks. */
export function BeatRow({ count, nowIndex, opened = false, waiting = false }: BeatRowProps) {
  return (
    <Box
      aria-hidden="true"
      data-opened={opened}
      data-testid={TEST_IDS.beatRow}
      sx={{ display: "flex", gap: `${beatGap(count)}px`, height: ROW_HEIGHT }}
    >
      {Array.from({ length: count }, (_, index) => (
        <Block key={index} opened={opened} pulsing={waiting && index === nowIndex} state={stateOf(index, nowIndex)} />
      ))}
    </Box>
  );
}

function stateOf(index: number, nowIndex: number | undefined): BeatState {
  if (nowIndex === undefined || index > nowIndex) {
    return "to-come";
  }

  return index === nowIndex ? "now" : "done";
}

/**
 * The block and its two halves are both always there, so that opening is a fade and a slide, which
 * cost nothing to animate. Closing again, for the next exercise, is immediate.
 */
function Block({
  opened,
  pulsing,
  state,
}: {
  readonly opened: boolean;
  readonly pulsing: boolean;
  readonly state: BeatState;
}) {
  const half = {
    backgroundColor: opened ? "var(--dd-accent)" : "var(--dd-ink)",
    height: HALF_HEIGHT,
    left: 0,
    opacity: opened ? 1 : 0,
    position: "absolute",
    right: 0,
    transition: opened ? `transform ${OPENING}, background-color ${OPENING}, opacity ${OPENING}` : "none",
  } as const;

  return (
    <Box sx={{ flex: 1, position: "relative" }}>
      <Box
        sx={{
          ...BLOCK_STYLES[state],
          animation: pulsing ? `${pulse} 1.4s ease-in-out infinite` : "none",
          border: "2px solid",
          borderRadius: "5px",
          boxSizing: "border-box",
          inset: 0,
          opacity: opened ? 0 : 1,
          position: "absolute",
          transition: opened
            ? `opacity ${OPENING}`
            : "background-color var(--dd-fast) var(--dd-ease), border-color var(--dd-fast) var(--dd-ease)",
        }}
      />
      <Box
        sx={{
          ...half,
          borderRadius: "5px 5px 0 0",
          top: 0,
          transform: opened ? "none" : `translateY(${SEAM_OFFSET}px)`,
        }}
      />
      <Box
        sx={{
          ...half,
          borderRadius: "0 0 5px 5px",
          bottom: 0,
          transform: opened ? "none" : `translateY(-${SEAM_OFFSET}px)`,
        }}
      />
    </Box>
  );
}
