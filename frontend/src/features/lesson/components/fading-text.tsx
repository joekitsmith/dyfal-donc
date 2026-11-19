import Box from "@mui/material/Box";
import { type CSSObject, keyframes } from "@mui/material/styles";
import { type RefCallback, useState } from "react";

import { MEDIA, MOTION } from "@/theme/tokens";

type FadingTextProps = {
  /** How long the text that is replaced takes to fade, as a CSS time. The new text always fades in over the base time. */
  readonly fadeOut: string;
  /** Sizes the paragraph of the text that is showing. */
  readonly fit?: RefCallback<HTMLElement>;
  readonly lang?: string;
  /** Sets `aria-live` on the region, so a screen reader says each new text once. */
  readonly live?: boolean;
  readonly sx?: CSSObject;
  /** Present on the text that is showing and not the one on its way out, so a test finds one element. */
  readonly testId?: string;
  readonly text: string;
};

type Layer = {
  /** The first text is there from the start, and does not fade in. */
  readonly animate: boolean;
  readonly id: number;
  readonly text: string;
};

const fadeIn = keyframes({ from: { opacity: 0 } });
const fadeOut = keyframes({ to: { opacity: 0 } });

/**
 * Text that fades in when it changes while the text it replaces fades out over it. The paragraph
 * showing is always there, even when it is empty, so the region it is in has something to announce into.
 */
export function FadingText({ fadeOut: fadeOutTime, fit, lang, live = false, sx, testId, text }: FadingTextProps) {
  const [layers, setLayers] = useState<readonly Layer[]>([{ animate: false, id: 0, text }]);
  const current = layers.at(-1);

  if (current === undefined) {
    throw new Error("The text has no layers");
  }

  if (current.text !== text) {
    // Something that was never shown has nothing to fade out
    const staying = current.text === "" ? layers.slice(0, -1) : layers;

    setLayers([...staying, { animate: true, id: current.id + 1, text }]);
  }

  return (
    <Box aria-live={live ? "polite" : undefined} sx={{ position: "relative" }}>
      {layers.map((layer, index) => {
        const showing = index === layers.length - 1;

        return (
          <Box
            aria-hidden={showing ? undefined : true}
            component="p"
            data-testid={showing ? testId : undefined}
            key={layer.id}
            lang={lang}
            onAnimationEnd={
              showing
                ? undefined
                : () => {
                    setLayers((previous) => previous.filter((other) => other.id !== layer.id));
                  }
            }
            ref={showing ? fit : undefined}
            sx={{
              ...sx,
              ...(showing
                ? { animation: layer.animate ? `${fadeIn} var(--dd-base) var(--dd-ease)` : "none" }
                : {
                    animation: `${fadeOut} ${fadeOutTime} var(--dd-ease) forwards`,
                    left: 0,
                    [MEDIA.reducedMotion]: { animationDuration: MOTION.fast },
                    pointerEvents: "none",
                    position: "absolute",
                    right: 0,
                    top: 0,
                  }),
            }}
          >
            {layer.text}
          </Box>
        );
      })}
    </Box>
  );
}
