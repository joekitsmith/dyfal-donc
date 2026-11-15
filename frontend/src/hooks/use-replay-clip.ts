import { useEffect, useRef, useState } from "react";

import { fetchClip } from "@/api/clips";

/** Plays one recording at a time, from a link the API gave. Starting another stops the first. */
export function useReplayClip() {
  const audio = useRef<HTMLAudioElement | null>(null);
  const url = useRef<null | string>(null);
  const [failed, setFailed] = useState(false);

  function stop() {
    audio.current?.pause();
    audio.current = null;

    if (url.current !== null) {
      URL.revokeObjectURL(url.current);
      url.current = null;
    }
  }

  useEffect(() => stop, []);

  return {
    failed,
    play: (path: string) => {
      stop();
      setFailed(false);
      fetchClip(path)
        .then(({ blob }) => {
          url.current = URL.createObjectURL(blob);
          audio.current = new Audio(url.current);

          return audio.current.play();
        })
        .catch(() => {
          setFailed(true);
        });
    },
  };
}
