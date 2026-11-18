import type { Overview } from "@/features/learning-session";

export type HomeCardsContent = {
  /** Set when the overview could not be loaded. */
  readonly error: null | { readonly retry: () => void };
  readonly everythingMet: boolean;
  readonly guest: boolean;
  readonly howItGoes: boolean;
  readonly recap: Overview["latest_session"];
};
