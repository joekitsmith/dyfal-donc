import { useEffect, useEffectEvent, useState } from "react";

import { beatIndexAt, type ThinkWindow } from "../utils/beats";

/**
 * The block the beat row is on while the learner thinks. It follows the audio's position a frame
 * at a time and not a timer, so it stays right when frames are held back, as they are with the
 * screen locked: the first frame after says where the audio has got to.
 *
 * `run` names one pass through the think time. A new one starts again from the first block, rather
 * than showing for a frame where the last one ended.
 */
export function useBeatIndex({
  count,
  counting,
  read,
  run,
}: {
  readonly count: number;
  readonly counting: boolean;
  readonly read: () => null | ThinkWindow;
  readonly run: string;
}): number {
  const [reached, setReached] = useState({ index: 0, run });
  const readThink = useEffectEvent(read);

  useEffect(() => {
    if (!counting) {
      return;
    }

    let frame = 0;
    const onFrame = () => {
      const window = readThink();

      if (window !== null) {
        const index = beatIndexAt(window, count);

        setReached((previous) => (previous.index === index && previous.run === run ? previous : { index, run }));
      }

      frame = requestAnimationFrame(onFrame);
    };

    frame = requestAnimationFrame(onFrame);

    return () => {
      cancelAnimationFrame(frame);
    };
  }, [count, counting, run]);

  return reached.run === run ? reached.index : 0;
}
