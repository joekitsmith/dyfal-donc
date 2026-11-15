import type { components } from "@/api/schema";

import type { ReportSubject } from "../types";

type Item = Pick<components["schemas"]["ItemDetailResponse"], "audio" | "english" | "id" | "welsh">;
type Sentence = components["schemas"]["SentenceResponse"];

/** A word or phrase, as something to report. A phrase has no audio. */
export function itemSubject(item: Item): ReportSubject {
  return { audio: item.audio, english: item.english, id: item.id, kind: "item", welsh: item.welsh };
}

/** A sentence the API gave, as something to report. */
export function sentenceSubject(sentence: Sentence): ReportSubject {
  return {
    audio: sentence.audio.welsh.standard,
    english: sentence.english,
    id: sentence.id,
    kind: "sentence",
    welsh: sentence.welsh,
  };
}
