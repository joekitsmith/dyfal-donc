import { type Dispatch, type RefObject, useEffect, useRef } from "react";

import type { LessonEvent, Timeline } from "../types";

import { reportPosition } from "../utils/media-session";
import { phaseAt } from "../utils/phase-at";
import { tailStart } from "../utils/tail-start";
import { type TrackPlayer } from "../utils/track-player";

/**
 * Tells the lesson where in the track it is, and when something else paused or resumed the audio.
 * A pause during the silent tail, when the lesson cannot pause, is undone: the exercise is about
 * to change and there is nothing to hold.
 */
export function useTrackPosition({
  canPause,
  dispatch,
  player,
  timelineRef,
}: {
  readonly canPause: boolean;
  readonly dispatch: Dispatch<LessonEvent>;
  readonly player: TrackPlayer;
  readonly timelineRef: RefObject<null | Timeline>;
}) {
  const canPauseNow = useRef(canPause);

  useEffect(() => {
    canPauseNow.current = canPause;
  });

  useEffect(
    () =>
      player.subscribe({
        onError: () => {
          dispatch({ type: "playback_failed" });
        },
        onPaused: () => {
          if (canPauseNow.current) {
            dispatch({ type: "pause" });
          } else {
            player.resume();
          }
        },
        onPlayed: () => {
          dispatch({ type: "resume" });
        },
        onPosition: () => {
          const timeline = timelineRef.current;

          if (timeline === null) {
            return;
          }

          dispatch({ phase: phaseAt(timeline, player.position), type: "position_reached" });

          if ("mediaSession" in navigator) {
            reportPosition(navigator.mediaSession, player.position, tailStart(timeline));
          }
        },
      }),
    [dispatch, player, timelineRef],
  );
}
