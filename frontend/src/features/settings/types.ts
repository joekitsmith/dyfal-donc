import type { LEARNING_SESSION_MINUTES } from "./constants";

export type LearningSessionMinutes = (typeof LEARNING_SESSION_MINUTES)[number];

export type UserSettings = {
  /** Null is no limit. */
  readonly learningSessionMinutes: LearningSessionMinutes | null;
  readonly slowWelshEnabled: boolean;
  readonly thinkTimeMultiplier: number;
};
