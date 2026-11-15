import { MEDIA_SESSION_ARTIST, MEDIA_SESSION_ARTWORK } from "../constants";

export type MediaSessionHandlers = {
  readonly missed: () => void;
  readonly pause: () => void;
  readonly play: () => void;
  readonly replay: () => void;
};

export type MediaSessionLike = Pick<
  MediaSession,
  "metadata" | "playbackState" | "setActionHandler" | "setPositionState"
>;

/** Seeking means nothing in an exercise, and phones show skip-by-10-seconds buttons instead of previous and next if it is set. */
const UNUSED_ACTIONS = ["seekbackward", "seekforward", "seekto"] as const;

/**
 * The lock screen and headphones: play and pause, previous replays the exercise, and next marks
 * it missed. Returns the function that takes it all away again.
 */
export function registerMediaSession(session: MediaSessionLike, handlers: MediaSessionHandlers): () => void {
  const actions: readonly (readonly [MediaSessionAction, (() => void) | null])[] = [
    ["play", handlers.play],
    ["pause", handlers.pause],
    ["previoustrack", handlers.replay],
    ["nexttrack", handlers.missed],
    ...UNUSED_ACTIONS.map((action) => [action, null] as const),
  ];

  for (const [action, handler] of actions) {
    setHandler(session, action, handler);
  }

  return () => {
    for (const [action] of actions) {
      setHandler(session, action, null);
    }

    session.metadata = null;
    session.playbackState = "none";
  };
}

/** What the lock screen shows. It is only ever the English, so it can never give the Welsh away. */
export function lessonMetadata(english: string): MediaMetadataInit {
  return { artist: MEDIA_SESSION_ARTIST, artwork: [...MEDIA_SESSION_ARTWORK], title: english };
}

// A browser throws for an action it does not know, and the rest should still be set
function setHandler(session: MediaSessionLike, action: MediaSessionAction, handler: (() => void) | null): void {
  try {
    session.setActionHandler(action, handler);
  } catch {
    // Not supported here
  }
}

/**
 * Where the lock screen's progress bar is. Without this it measures the whole audio, silent tail
 * included, so the bar runs long and jumps at the end. The duration is where the tail starts.
 */
export function reportPosition(session: MediaSessionLike, seconds: number, duration: number): void {
  try {
    session.setPositionState({ duration, playbackRate: 1, position: Math.min(Math.max(seconds, 0), duration) });
  } catch {
    // Not supported here
  }
}
