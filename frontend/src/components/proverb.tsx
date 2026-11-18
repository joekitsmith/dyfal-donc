import Box from "@mui/material/Box";

import { textStyle } from "@/theme/text-style";

type ProverbProps = { readonly language: "cy" | "en" };

const WELSH_BOX_HEIGHT = 76;

/** The English goes in the frame's English box. The Welsh has a box of its own, so what is below it stays put. */
export function Proverb({ language }: ProverbProps) {
  if (language === "en") {
    return <p>Persistent tapping breaks the stone</p>;
  }

  return (
    <Box sx={{ ...textStyle("sentence-cy"), flexShrink: 0, height: WELSH_BOX_HEIGHT, overflow: "hidden" }}>
      <Box component="p" lang="cy" sx={{ m: 0 }}>
        Dyfal donc a dyr y garreg
      </Box>
    </Box>
  );
}
