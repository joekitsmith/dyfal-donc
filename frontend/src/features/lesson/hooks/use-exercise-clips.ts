import { type Dispatch, useCallback, useEffect, useRef } from "react";

import { fetchClip } from "@/api/clips";

import type { ClipTrack, LessonEvent, LessonExercise } from "../types";

import { CLIP_TRACKS } from "../constants";
import { failureCause } from "../utils/failure-cause";

/**
 * Fetches the exercise's clips (the slow Welsh only if it will play) in parallel as soon as it is known and keeps them as object URLs,
 * so replays never ask the server again. Passing null (the exercise is over) revokes them.
 */
export function useExerciseClips(
  exercise: LessonExercise | null,
  attempt: number,
  includeSlowWelsh: boolean,
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
      if (track === "welsh_slow" && !includeSlowWelsh) {
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
  }, [attempt, dispatch, exercise, includeSlowWelsh]);

  return useCallback((track: ClipTrack) => urls.current.get(track), []);
}
