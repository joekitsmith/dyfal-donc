import type { components } from "@/api/schema";

export type ReportCategory = components["schemas"]["ProblemCategory"];

/** The form as it is filled in. The category is empty until one is chosen. */
export type ReportFormValues = {
  readonly category: string;
  readonly description: string;
  /** Which of the subjects is reported, or ``NO_SUBJECT`` for none of them. */
  readonly subjectId: string;
};

/** The form once it has passed the schema. */
export type ReportValues = {
  readonly category: ReportCategory;
  readonly description: string;
  readonly subjectId: string;
};

export type ReportSource = components["schemas"]["ProblemSource"];

/** The sentence, word or phrase a report is about. ``audio`` is the standard Welsh, if there is any. */
export type ReportSubject = {
  readonly audio: null | string;
  readonly english: string;
  readonly id: string;
  readonly kind: "item" | "sentence";
  readonly welsh: string;
};
