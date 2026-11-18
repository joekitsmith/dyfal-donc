import Box from "@mui/material/Box";

import { TEST_IDS } from "@/config/test-ids";

type SentenceBoxProps = { readonly english: string };

/** The paragraph is always there, so a screen reader announces the sentence once, when it arrives. */
export function SentenceBox({ english }: SentenceBoxProps) {
  return (
    <Box aria-live="polite">
      <Box component="p" data-testid={TEST_IDS.english} lang="en" sx={{ m: 0 }}>
        {english}
      </Box>
    </Box>
  );
}
