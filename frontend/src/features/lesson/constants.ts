export const CLIP_TRACKS = ["english", "welsh", "welsh_slow"] as const;

export const THINK_BASE_SECONDS = 2.7;
export const THINK_SECONDS_PER_WORD = 0.9;
export const THINK_MAXIMUM_SECONDS = 27;

export const THINK_MULTIPLIER_DEFAULT = 1;
export const THINK_MULTIPLIER_MINIMUM = 0.5;
export const THINK_MULTIPLIER_MAXIMUM = 3;
export const THINK_MULTIPLIER_STEP = 0.25;
export const THINK_MULTIPLIER_STORAGE_KEY = "dyfal-donc.think-time-multiplier";

/** After the first Welsh: this long until its text shows, then this long until the slow Welsh. */
export const BETWEEN_WELSH_REVEAL_MILLISECONDS = 1000;
export const BETWEEN_WELSH_READING_MILLISECONDS = 500;

/** How long the learner has to mark an exercise as missed after the slow Welsh ends. */
export const OUTCOME_WINDOW_MILLISECONDS = 2000;

export const CLIP_ERROR_MESSAGE = "The audio could not be loaded";
export const PLAYBACK_ERROR_MESSAGE = "The audio could not be played";
export const NEXT_ERROR_MESSAGE = "The next exercise could not be loaded";
export const SUBMIT_ERROR_MESSAGE = "Your answer could not be saved";

export const ALREADY_ANSWERED_STATUS = 409;
export const SELECTION_EXPIRED_STATUS = 410;
