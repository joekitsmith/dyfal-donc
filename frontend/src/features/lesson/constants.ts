export const CLIP_TRACKS = ["english", "welsh", "welsh_slow"] as const;

export const THINK_BASE_SECONDS = 2.16;
export const THINK_SECONDS_PER_WORD = 0.72;
export const THINK_MAXIMUM_SECONDS = 21.6;

export const THINK_MULTIPLIER_DEFAULT = 1;
export const THINK_MULTIPLIER_MINIMUM = 0.5;
export const THINK_MULTIPLIER_MAXIMUM = 3;
export const THINK_MULTIPLIER_STEP = 0.25;
export const THINK_MULTIPLIER_STORAGE_KEY = "dyfal-donc.think-time-multiplier";

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
  "Your progress was not found on the server. The course may have been reset, so start over to carry on.";
export const SPEECH_UNAVAILABLE_MESSAGE = "The speech service is not available. Check that it is running, then retry.";
export const NOTHING_ELIGIBLE_MESSAGE =
  "The course is not ready for you yet. There is a gap in the content, so there is nothing to give you right now. Try refreshing later.";

export const NOT_FOUND_STATUS = 404;
export const SERVICE_UNAVAILABLE_STATUS = 503;

export const ALREADY_ANSWERED_STATUS = 409;
export const SELECTION_EXPIRED_STATUS = 410;
