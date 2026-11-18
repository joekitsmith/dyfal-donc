import Box from "@mui/material/Box";

import { TEST_IDS } from "@/config/test-ids";
import { textStyle } from "@/theme/text-style";

import type { LessonView } from "../utils/lesson-view";

import { LessonError } from "./lesson-error";
import { NextButton } from "./next-button";

type WelshAreaProps = {
  readonly actions: { readonly onNext: () => void; readonly onRetry: () => void };
  readonly view: LessonView;
};

const AREA_HEIGHT = 170;

/**
 * Where the Welsh will be. It has a fixed height, so nothing below it moves when the sentence
 * appears. The caption is above the sentence until it is shown, and below it after.
 */
export function WelshArea({ actions, view }: WelshAreaProps) {
  const shown = view.welsh !== "";
  const caption =
    view.caption === null ? null : (
      <Box
        aria-hidden="true"
        data-testid={TEST_IDS.caption}
        sx={{ ...textStyle(shown ? "caption-small" : "caption"), color: "var(--dd-muted)", mt: shown ? "14px" : 0 }}
      >
        {view.caption}
      </Box>
    );

  return (
    <Box sx={{ flexShrink: 0, height: AREA_HEIGHT, position: "relative" }}>
      {shown ? null : caption}
      <Box aria-live="polite">
        <Box component="p" data-testid={TEST_IDS.welsh} lang="cy" sx={{ ...textStyle("sentence-cy"), m: 0 }}>
          {view.welsh}
        </Box>
      </Box>
      {shown ? caption : null}
      {/* Said aloud by a screen reader, where the caption itself is left out because the audio says it */}
      <Box role="status" sx={VISUALLY_HIDDEN}>
        {view.paused ? "Paused" : ""}
      </Box>
      {view.error === null ? null : <LessonError error={view.error} onRetry={actions.onRetry} />}
      {view.next ? (
        <Box sx={{ bottom: 0, position: "absolute", right: 0 }}>
          <NextButton onClick={actions.onNext} />
        </Box>
      ) : null}
    </Box>
  );
}

const VISUALLY_HIDDEN = {
  clip: "rect(0 0 0 0)",
  height: 1,
  overflow: "hidden",
  position: "absolute",
  whiteSpace: "nowrap",
  width: 1,
} as const;
