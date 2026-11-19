import type { ReportCategory } from "./types";

export const DESCRIPTION_MAXIMUM_LENGTH = 1000;

/** The subject id of a report that is not about any of the sentences offered. */
export const NO_SUBJECT = "";
export const NO_SUBJECT_LABEL = "Not about one of these sentences";
export const SUBJECT_LEGEND = "Which sentence?";

export const TOO_MANY_REPORTS_STATUS = 429;

export const SEND_FAILED_MESSAGE = "The report couldn't be sent.";
export const TOO_MANY_REPORTS_MESSAGE = "Too many reports. Try again in a minute.";

/** In the order the dropdown shows them. */
export const CATEGORY_OPTIONS: readonly { readonly label: string; readonly value: ReportCategory }[] = [
  { label: "The English doesn't match the Welsh", value: "wrong_translation" },
  { label: "Nobody would say it like this", value: "unnatural" },
  { label: "Grammar (including tense and word order)", value: "grammar" },
  { label: "A mutation is wrong", value: "mutation" },
  { label: "Spelling or punctuation", value: "spelling_or_punctuation" },
  { label: "Not South Wales Welsh", value: "not_south_wales" },
  { label: "Sounds wrong when spoken", value: "sounds_wrong" },
  { label: "The audio is broken (cut off or garbled)", value: "audio_broken" },
  { label: "The English wording is odd", value: "english_wording" },
  { label: "Other", value: "other" },
];
