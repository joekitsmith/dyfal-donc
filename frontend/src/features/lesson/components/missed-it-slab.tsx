import Box from "@mui/material/Box";
import ButtonBase from "@mui/material/ButtonBase";

import { TickIcon } from "@/components/icons/tick-icon";
import { TEST_IDS } from "@/config/test-ids";
import { textStyle } from "@/theme/text-style";

import type { LessonView } from "../utils/lesson-view";

type MissedItSlabProps = {
  readonly onPress: () => void;
  readonly state: LessonView["slab"];
};

const SLAB_HEIGHT = 88;

const STATE_STYLES = {
  available: {
    backgroundColor: "var(--dd-inverse-bg)",
    border: "2px solid var(--dd-inverse-bg)",
    color: "var(--dd-inverse-fg)",
  },
  marked: {
    backgroundColor: "var(--dd-surface)",
    border: "2px solid var(--dd-accent)",
    color: "var(--dd-ink)",
  },
  waiting: {
    backgroundColor: "transparent",
    border: "2px dashed var(--dd-line)",
    color: "var(--dd-muted)",
  },
} as const;

const SECOND_LINES = {
  available: "Bring this one back sooner",
  marked: "It'll come back sooner. Nothing else changes.",
  waiting: "Ready once you've heard the Welsh",
} as const;

/** One button in all three states, so that it never moves and a press is never lost to a re-render. */
export function MissedItSlab({ onPress, state }: MissedItSlabProps) {
  return (
    <ButtonBase
      aria-disabled={state === "waiting" ? true : undefined}
      aria-pressed={state === "marked" ? true : undefined}
      data-testid={TEST_IDS.missedIt}
      onClick={onPress}
      sx={{
        ...STATE_STYLES[state],
        "&:active": { transform: "scale(0.98)" },
        borderRadius: "10px",
        flexDirection: "column",
        flexShrink: 0,
        gap: "2px",
        height: SLAB_HEIGHT,
        justifyContent: "center",
        transition:
          "background-color var(--dd-fast) var(--dd-ease), color var(--dd-fast) var(--dd-ease), border-color var(--dd-fast) var(--dd-ease), transform var(--dd-fast) var(--dd-ease)",
        width: "100%",
      }}
    >
      <Box component="span" sx={{ ...textStyle("title"), alignItems: "center", display: "flex", gap: "8px" }}>
        {state === "marked" ? (
          <Box component="span" sx={{ color: "var(--dd-accent)", display: "flex" }}>
            <TickIcon size={22} />
          </Box>
        ) : null}
        {state === "marked" ? "Marked" : "Missed it"}
      </Box>
      <Box component="span" sx={textStyle("hint")}>
        {SECOND_LINES[state]}
      </Box>
    </ButtonBase>
  );
}
