/** What clip fetching assumes when no exercise is showing. */
export const DEFAULT_WELSH_PLAYBACK = "both";

/** How many exercises the lesson remembers for a problem report: the current one and two before it. */
export const MAX_RECENT_EXERCISES = 3;

export const CLIP_TRACKS = ["english", "welsh_standard", "welsh_slow"] as const;

export const THINK_BASE_SECONDS = 2.16;
export const THINK_SECONDS_PER_WORD = 0.72;
export const THINK_MAXIMUM_SECONDS = 21.6;

/** The gap after the first Welsh. Its text shows, and the slow Welsh starts, when it ends. */
export const BETWEEN_WELSH_SECONDS = 1.5;

/** How long the handover to the next exercise can take before the screen stops pretending nothing is happening. */
export const HANDOVER_VISIBLE_MILLISECONDS = 1500;

/** How long the learner has to mark an exercise as missed after the slow Welsh ends. */
export const OUTCOME_WINDOW_SECONDS = 2;

/**
 * Silence after the outcome window. The track keeps playing while the outcome is sent and the next
 * exercise is fetched and built, which is what keeps the page alive with the screen locked.
 */
export const TAIL_SECONDS = 10;

/** How often the audio position is read as well as on `timeupdate`, which is the only thing that runs reliably when locked. */
export const POSITION_POLL_MILLISECONDS = 250;

/** The waits before each retry of a request, so a brief failure while the screen is locked does not stop the lesson. */
export const RETRY_DELAYS_MILLISECONDS = [1000, 2000] as const;

/** The silent clip that unlocks audio on Start. */
export const SILENT_SAMPLE_RATE = 8000;
export const SILENT_SAMPLES = 400;

export const MEDIA_SESSION_ARTIST = "dyfal-donc";
export const MEDIA_SESSION_ARTWORK = [
  { sizes: "512x512", src: "/icons/icon-512.png", type: "image/png" },
  { sizes: "192x192", src: "/icons/icon-192.png", type: "image/png" },
] as const;

/** What the error card says: a title, and one line on what to do. */
export const LESSON_ERRORS = {
  clips: { text: "Check your connection, then try again.", title: "The audio couldn't be loaded" },
  learner_missing: {
    text: "It isn't on the server any more. To carry on, delete this account and start again.",
    title: "We couldn't find your progress",
  },
  next: { text: "Check your connection, then try again.", title: "The next sentence couldn't be loaded" },
  nothing_eligible: { text: "Please come back a little later.", title: "The course isn't ready yet" },
  playback: { text: "Try again to restart this sentence.", title: "The audio couldn't be played" },
  speech_unavailable: {
    text: "It usually comes back within a few minutes.",
    title: "The speech service isn't available",
  },
  submit: {
    text: "Check your connection, then try again. Nothing is lost.",
    title: "Your answer couldn't be saved",
  },
} as const;

export const NOT_FOUND_STATUS = 404;
export const UNAUTHORIZED_STATUS = 401;

/** Items introduced before a guest is asked to add a passkey: about ten exercises in. */
export const SAVE_OFFER_MINIMUM_ITEMS = 5;
export const SERVICE_UNAVAILABLE_STATUS = 503;
export const SERVER_ERROR_STATUS = 500;

export const ALREADY_ANSWERED_STATUS = 409;
export const SELECTION_EXPIRED_STATUS = 410;
