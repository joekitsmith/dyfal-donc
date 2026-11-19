import Box from "@mui/material/Box";

import { BeatRow } from "@/components/beat-row";
import { textStyle } from "@/theme/text-style";
import { thinkSeconds } from "@/utils/think-time";

type ThinkTimePreviewProps = { readonly multiplier: number };

const EXAMPLE_SENTENCE = "un dau tri pedwar";
/** The words of the example, and the three blocks every sentence has besides. */
const EXAMPLE_BLOCKS = 7;
const BLOCKS_DONE = 2;
const PREVIEW_HEIGHT = 32;

/** What the setting comes to for a sentence of four words: how long the learner gets, and how long each block lasts. */
export function ThinkTimePreview({ multiplier }: ThinkTimePreviewProps) {
  const seconds = thinkSeconds(EXAMPLE_SENTENCE, multiplier);

  return (
    <Box sx={{ mt: "16px" }}>
      <BeatRow count={EXAMPLE_BLOCKS} height={PREVIEW_HEIGHT} nowIndex={BLOCKS_DONE} />
      <Box sx={{ ...textStyle("body"), mt: "8px" }}>
        A four-word sentence gets {seconds.toFixed(1)} seconds. Each block lasts {(seconds / EXAMPLE_BLOCKS).toFixed(1)}{" "}
        seconds.
      </Box>
    </Box>
  );
}
