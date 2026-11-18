import { useEffect, useRef } from "react";

import { recordHeadphoneUse } from "@/features/home";

import type { LessonActions } from "./use-lesson-player";

import { lessonMetadata, registerMediaSession } from "../utils/media-session";

/**
 * The lock screen, headphones and car controls for the lesson. The title is the English of the
 * exercise playing. The next exercise's is not shown while the last one's silent tail plays.
 */
export function useLessonMediaSession({
  actions,
  active,
  english,
  paused,
}: {
  readonly actions: LessonActions;
  readonly active: boolean;
  /** Null while there is no exercise playing. */
  readonly english: null | string;
  readonly paused: boolean;
}) {
  const latest = useRef(actions);

  // The handlers are set once and always run the latest actions
  useEffect(() => {
    latest.current = actions;
  });

  useEffect(() => {
    if (!active || !("mediaSession" in navigator)) {
      return;
    }

    return registerMediaSession(navigator.mediaSession, {
      missed: () => {
        recordHeadphoneUse();
        latest.current.missed();
      },
      pause: () => {
        recordHeadphoneUse();
        latest.current.pause();
      },
      play: () => {
        recordHeadphoneUse();
        latest.current.resume();
      },
      replay: () => {
        recordHeadphoneUse();
        latest.current.replay();
      },
    });
  }, [active]);

  useEffect(() => {
    if (active && english !== null && "mediaSession" in navigator) {
      navigator.mediaSession.metadata = new MediaMetadata(lessonMetadata(english));
    }
  }, [active, english]);

  useEffect(() => {
    if (active && "mediaSession" in navigator) {
      navigator.mediaSession.playbackState = paused ? "paused" : "playing";
    }
  }, [active, paused]);
}
