import { type Dispatch, useCallback, useEffect, useRef } from "react";

import { fetchClip } from "@/api/clips";

import type { ClipTrack, LessonEvent, LessonExercise } from "../types";

import { CLIP_TRACKS } from "../constants";

/**
 * Fetches the exercise's clips in parallel as soon as it is known and keeps them as object URLs,
 * so replays never ask the server again. Passing null (the exercise is over) revokes them.
 */
export function useExerciseClips(exercise: LessonExercise | null, attempt: number, dispatch: Dispatch<LessonEvent>) {
  const urls = useRef(new Map<ClipTrack, string>());

  useEffect(() => {
    if (exercise === null) {
      return;
    }

    const controller = new AbortController();
    const loaded = new Map<ClipTrack, string>();

    urls.current = loaded;

    for (const track of CLIP_TRACKS) {
      fetchClip(exercise.audio[track], { signal: controller.signal })
        .then((clip) => {
          if (controller.signal.aborted) {
            return;
          }

          loaded.set(track, URL.createObjectURL(clip.blob));
          console.info(`Clip ${track}: ${clip.milliseconds.toFixed(0)} ms`);
          dispatch({ track, type: "clip_ready" });
        })
        .catch(() => {
          if (!controller.signal.aborted) {
            dispatch({ track, type: "clip_failed" });
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
  }, [attempt, dispatch, exercise]);

  return useCallback((track: ClipTrack) => urls.current.get(track), []);
}
