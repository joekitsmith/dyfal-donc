import Box from "@mui/material/Box";

import { beatGap } from "@/utils/beat-gap";

type BeatRowProps = {
  readonly count: number;
  /** Blocks before it are done and blocks after it are to come. Without it, all are to come. */
  readonly nowIndex?: number;
  /** Each block splits along a seam, which is how the row shows that the Welsh has been said. */
  readonly opened?: boolean;
};

type BeatState = "done" | "now" | "to-come";

const ROW_HEIGHT = 48;
const HALF_HEIGHT = 20;

const BLOCK_STYLES = {
  done: { backgroundColor: "var(--dd-ink)", borderColor: "var(--dd-ink)" },
  now: { backgroundColor: "var(--dd-accent)", borderColor: "var(--dd-accent)" },
  "to-come": { backgroundColor: "transparent", borderColor: "var(--dd-line)" },
} as const;

/** The time the learner has to speak, drawn as blocks. */
export function BeatRow({ count, nowIndex, opened = false }: BeatRowProps) {
  return (
    <Box aria-hidden="true" sx={{ display: "flex", gap: `${beatGap(count)}px`, height: ROW_HEIGHT }}>
      {Array.from({ length: count }, (_, index) =>
        opened ? (
          <OpenedBlock key={index} />
        ) : (
          <Box
            key={index}
            sx={{
              ...BLOCK_STYLES[stateOf(index, nowIndex)],
              border: "2px solid",
              borderRadius: "5px",
              boxSizing: "border-box",
              flex: 1,
              transition: "background-color var(--dd-fast) var(--dd-ease), border-color var(--dd-fast) var(--dd-ease)",
            }}
          />
        ),
      )}
    </Box>
  );
}

function stateOf(index: number, nowIndex: number | undefined): BeatState {
  if (nowIndex === undefined || index > nowIndex) {
    return "to-come";
  }

  return index === nowIndex ? "now" : "done";
}

function OpenedBlock() {
  const half = { backgroundColor: "var(--dd-accent)", height: HALF_HEIGHT };

  return (
    <Box sx={{ display: "flex", flex: 1, flexDirection: "column", gap: "8px" }}>
      <Box sx={{ ...half, borderRadius: "5px 5px 0 0" }} />
      <Box sx={{ ...half, borderRadius: "0 0 5px 5px" }} />
    </Box>
  );
}
