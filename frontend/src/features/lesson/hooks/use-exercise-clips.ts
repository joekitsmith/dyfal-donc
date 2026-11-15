import { type Dispatch, useCallback, useEffect, useRef } from "react";

import { fetchClip } from "@/api/clips";

import type { ClipTrack, LessonEvent, LessonExercise, WelshPlayback } from "../types";

import { CLIP_TRACKS } from "../constants";
import { failureCause } from "../utils/failure-cause";

/**
 * Fetches the exercise's clips (the Welsh ones only if they will play) in parallel as soon as it is known and keeps them as object URLs,
 * so replays never ask the server again. Passing null (the exercise is over) revokes them.
 */
export function useExerciseClips(
  exercise: LessonExercise | null,
  attempt: number,
  welshPlayback: WelshPlayback,
  dispatch: Dispatch<LessonEvent>,
) {
  const urls = useRef(new Map<ClipTrack, string>());

  useEffect(() => {
    if (exercise === null) {
      return;
    }

    const controller = new AbortController();
    const loaded = new Map<ClipTrack, string>();

    urls.current = loaded;

    for (const track of CLIP_TRACKS) {
      if (!isPlayed(track, welshPlayback)) {
        continue;
      }

      fetchClip(exercise.audio[track], { signal: controller.signal })
        .then((clip) => {
          if (controller.signal.aborted) {
            return;
          }

          loaded.set(track, URL.createObjectURL(clip.blob));
          console.info(`Clip ${track}: ${clip.milliseconds.toFixed(0)} ms`);
          dispatch({ track, type: "clip_ready" });
        })
        .catch((error: unknown) => {
          if (!controller.signal.aborted) {
            dispatch({ cause: failureCause(error), track, type: "clip_failed" });
          }
        });
    }

    return () => {
      controller.abort();

      for (const url of loaded.values()) {
        URL.revokeObjectURL(url);
      }

      loaded.clear();
    };
  }, [attempt, dispatch, exercise, welshPlayback]);

  return useCallback((track: ClipTrack) => urls.current.get(track), []);
}

function isPlayed(track: ClipTrack, welshPlayback: WelshPlayback): boolean {
  if (track === "welsh_standard") {
    return welshPlayback !== "slow";
  }

  return track === "welsh_slow" ? welshPlayback !== "standard" : true;
}
