import { useEffect, useRef, useState } from "react";

import { fetchClip } from "@/api/clips";

const FAILURE_VISIBLE_MILLISECONDS = 4000;

/**
 * Plays one recording at a time, from a link the API gave. Starting another stops the first, and
 * playing the one that is playing stops it. A failure is remembered for a few seconds against the
 * recording that failed, so the screen can say which.
 */
export function useReplayClip() {
  const audio = useRef<HTMLAudioElement | null>(null);
  const url = useRef<null | string>(null);
  const failureTimer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
  // Tells a request that has been overtaken, by another press or by leaving, to do nothing
  const latest = useRef(0);
  const [playing, setPlaying] = useState<null | string>(null);
  const [failed, setFailed] = useState<null | string>(null);

  function release() {
    latest.current += 1;
    audio.current?.pause();
    audio.current = null;

    if (url.current !== null) {
      URL.revokeObjectURL(url.current);
      url.current = null;
    }
  }

  useEffect(
    () => () => {
      release();
      clearTimeout(failureTimer.current);
    },
    [],
  );

  return {
    failed,
    play: (path: string) => {
      const stopping = playing === path;

      release();
      clearTimeout(failureTimer.current);
      setFailed(null);

      if (stopping) {
        setPlaying(null);

        return;
      }

      const request = latest.current;

      setPlaying(path);
      fetchClip(path)
        .then(({ blob }) => {
          if (request !== latest.current) {
            return;
          }

          url.current = URL.createObjectURL(blob);
          audio.current = new Audio(url.current);
          audio.current.addEventListener("ended", () => {
            if (request === latest.current) {
              setPlaying(null);
            }
          });

          return audio.current.play();
        })
        .catch(() => {
          if (request !== latest.current) {
            return;
          }

          setPlaying(null);
          setFailed(path);
          failureTimer.current = setTimeout(() => {
            setFailed(null);
          }, FAILURE_VISIBLE_MILLISECONDS);
        });
    },
    playing,
  };
}
