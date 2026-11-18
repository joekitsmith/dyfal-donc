import { type Dispatch, type RefObject, useEffect, useEffectEvent } from "react";

import { fetchClip } from "@/api/clips";
import { thinkSeconds } from "@/utils/think-time";

import type { ClipTrack, LessonEvent, LessonExercise, LessonSettings, Timeline, WelshPlayback } from "../types";

import { CLIP_TRACKS } from "../constants";
import { buildTrack } from "../utils/build-track";
import { failureCause } from "../utils/failure-cause";
import { type TrackPlayer } from "../utils/track-player";
import { parseWav, type WavClip } from "../utils/wav";
import { withRetry } from "../utils/with-retry";

/**
 * Fetches the exercise's clips (the Welsh ones only if they will play) as soon as it is known,
 * builds them into its track and plays that, in place of the one before. The one before is still
 * playing its silent tail until then, so nothing is heard to stop.
 */
export function useExerciseTrack({
  attempt,
  dispatch,
  exercise,
  player,
  settings,
  timelineRef,
  welshPlayback,
}: {
  readonly attempt: number;
  readonly dispatch: Dispatch<LessonEvent>;
  /** Null once the exercise is over, which stops anything still loading. */
  readonly exercise: LessonExercise | null;
  readonly player: TrackPlayer;
  readonly settings: LessonSettings;
  readonly timelineRef: RefObject<null | Timeline>;
  readonly welshPlayback: WelshPlayback;
}) {
  const thinkMultiplier = useEffectEvent(() => settings.thinkTimeMultiplier);

  useEffect(() => {
    if (exercise === null) {
      return;
    }

    const controller = new AbortController();
    const started = performance.now();

    fetchClips(exercise, welshPlayback, controller.signal)
      .then((clips) => {
        if (controller.signal.aborted) {
          return;
        }

        const track = buildTrack({
          clips,
          thinkSeconds: thinkSeconds(exercise.welsh, thinkMultiplier()),
          welshPlayback,
        });

        console.info(`Track ready: ${(performance.now() - started).toFixed(0)} ms`);
        timelineRef.current = track.timeline;
        player.play(URL.createObjectURL(track.blob));
        dispatch({ type: "track_ready" });
      })
      .catch((error: unknown) => {
        if (!controller.signal.aborted) {
          dispatch({ cause: failureCause(error), type: "track_failed" });
        }
      });

    return () => {
      controller.abort();
    };
  }, [attempt, dispatch, exercise, player, timelineRef, welshPlayback]);
}

async function fetchClips(
  exercise: LessonExercise,
  welshPlayback: WelshPlayback,
  signal: AbortSignal,
): Promise<Readonly<Partial<Record<ClipTrack, WavClip>>>> {
  const tracks = CLIP_TRACKS.filter((track) => isPlayed(track, welshPlayback));
  const clips = await Promise.all(
    tracks.map(async (track) => {
      const clip = await withRetry(() => fetchClip(exercise.audio[track], { signal }), signal);

      return parseWav(await clip.blob.arrayBuffer());
    }),
  );

  return Object.fromEntries(tracks.map((track, index) => [track, clips[index]]));
}

function isPlayed(track: ClipTrack, welshPlayback: WelshPlayback): boolean {
  if (track === "welsh_standard") {
    return welshPlayback !== "slow";
  }

  return track === "welsh_slow" ? welshPlayback !== "standard" : true;
}
