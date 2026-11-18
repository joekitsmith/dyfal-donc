import type { ReactNode } from "react";

import Box from "@mui/material/Box";

import { textStyle } from "@/theme/text-style";

type ScreenFrameProps = {
  readonly beats: ReactNode;
  /** Fills the space between the beat row and the controls, and scrolls if it does not fit. */
  readonly body: ReactNode;
  readonly controls: ReactNode;
  /** The box has a fixed height, so a sentence never moves what is below it. */
  readonly english: ReactNode;
  readonly header: ReactNode;
};

const COLUMN_WIDTH = 440;
const ENGLISH_BOX_HEIGHT = 76;

/** Keep the controls on screen on a short phone, and with the content in a tall window. */
const SHORT_VIEWPORT = "@media (max-height: 699px)";
const TALL_VIEWPORT = "@media (min-height: 901px)";
const TALL_FRAME_HEIGHT = 844;

/** The layout of the lesson, Home, Welcome and the message screens, so that moving between them changes the content and not the layout. */
export function ScreenFrame({ beats, body, controls, english, header }: ScreenFrameProps) {
  return (
    <Box sx={{ alignItems: "center", display: "flex", justifyContent: "center", minHeight: "100dvh" }}>
      <Box
        component="main"
        sx={{
          display: "flex",
          flexDirection: "column",
          height: "100dvh",
          maxWidth: COLUMN_WIDTH,
          pb: "max(28px, calc(env(safe-area-inset-bottom) + 12px))",
          px: "24px",
          [TALL_VIEWPORT]: { height: TALL_FRAME_HEIGHT },
          width: "100%",
        }}
      >
        {header}
        <Box
          sx={{
            ...textStyle("sentence-en"),
            "& > *": { font: "inherit", margin: 0 },
            flexShrink: 0,
            height: ENGLISH_BOX_HEIGHT,
            mt: "60px",
            overflow: "hidden",
            [SHORT_VIEWPORT]: { mt: "24px" },
          }}
        >
          {english}
        </Box>
        <Box sx={{ flexShrink: 0, mt: "28px", [SHORT_VIEWPORT]: { mt: "20px" } }}>{beats}</Box>
        <Box
          sx={{
            display: "flex",
            flex: 1,
            flexDirection: "column",
            minHeight: 0,
            mt: "28px",
            overflowY: "auto",
            [SHORT_VIEWPORT]: { mt: "20px" },
          }}
        >
          {body}
        </Box>
        <Box sx={{ display: "flex", flexDirection: "column", flexShrink: 0, gap: "12px" }}>{controls}</Box>
      </Box>
    </Box>
  );
}
