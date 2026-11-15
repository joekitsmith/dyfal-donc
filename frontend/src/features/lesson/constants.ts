/** What clip fetching assumes when no exercise is showing. */
export const DEFAULT_WELSH_PLAYBACK = "both";

export const CLIP_TRACKS = ["english", "welsh_standard", "welsh_slow"] as const;

export const THINK_BASE_SECONDS = 2.16;
export const THINK_SECONDS_PER_WORD = 0.72;
export const THINK_MAXIMUM_SECONDS = 21.6;

/** The gap after the first Welsh. Its text shows, and the slow Welsh starts, when it ends. */
export const BETWEEN_WELSH_MILLISECONDS = 1500;

/** How long the learner has to mark an exercise as missed after the slow Welsh ends. */
export const OUTCOME_WINDOW_MILLISECONDS = 2000;

export const ERROR_MESSAGES = {
  clips: "The audio could not be loaded",
  next: "The next exercise could not be loaded",
  playback: "The audio could not be played",
  submit: "Your answer could not be saved",
} as const;

export const LEARNER_MISSING_MESSAGE =
  "Your progress was not found on the server. The course may have been reset, so delete your account and start again.";
export const SPEECH_UNAVAILABLE_MESSAGE = "The speech service is not available. Check that it is running, then retry.";
export const NOTHING_ELIGIBLE_MESSAGE =
  "The course is not ready for you yet. There is a gap in the content, so there is nothing to give you right now. Try refreshing later.";

export const NOT_FOUND_STATUS = 404;
export const UNAUTHORIZED_STATUS = 401;

/** Items introduced before a guest is asked to add a passkey: about ten exercises in. */
export const SAVE_OFFER_MINIMUM_ITEMS = 5;
export const SERVICE_UNAVAILABLE_STATUS = 503;

export const ALREADY_ANSWERED_STATUS = 409;
export const SELECTION_EXPIRED_STATUS = 410;
