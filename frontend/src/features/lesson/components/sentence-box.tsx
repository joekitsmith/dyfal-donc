import type { RefCallback } from "react";

import { TEST_IDS } from "@/config/test-ids";

import { HANDOVER_FADE } from "../constants";
import { FadingText } from "./fading-text";

type SentenceBoxProps = { readonly english: string; readonly fit: RefCallback<HTMLElement> };

/** The paragraph is always there, so a screen reader announces the sentence once, when it arrives. */
export function SentenceBox({ english, fit }: SentenceBoxProps) {
  return (
    <FadingText
      fadeOut={HANDOVER_FADE}
      fit={fit}
      lang="en"
      live
      sx={{ m: 0 }}
      testId={TEST_IDS.english}
      text={english}
    />
  );
}
