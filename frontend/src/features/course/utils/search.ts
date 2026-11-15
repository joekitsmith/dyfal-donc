import type { SearchResult, TopicProgress } from "../types";

const COMBINING_MARKS = /[̀-ͯ]/gu;

/** Lower case with accents removed, so ŵ, ŷ and â match w, y and a. */
export function normaliseSearchText(text: string): string {
  return text.normalize("NFD").replaceAll(COMBINING_MARKS, "").toLowerCase().trim();
}

/** The words and phrases met whose English, Welsh or other forms contain the text, in teaching order. */
export function searchItems(topics: readonly TopicProgress[], query: string): readonly SearchResult[] {
  const wanted = normaliseSearchText(query);

  if (wanted === "") {
    return [];
  }

  return topics.flatMap((topic) =>
    [...topic.words, ...topic.phrases]
      .filter((item) =>
        [item.welsh, item.english, ...item.forms].some((text) => normaliseSearchText(text).includes(wanted)),
      )
      .map((item) => ({ item, topic: topic.name })),
  );
}
