import type { TopicProgress } from "../types";

function count(amount: number, singular: string, plural: string): string {
  return `${amount} ${amount === 1 ? singular : plural}`;
}

/** What the learner has met in the topic, such as "12 words · 4 ways of saying things". Ways of saying things are left out when there are none. */
export function describeTopic(topic: TopicProgress): string {
  const phrases = topic.phrases.length;

  return [
    count(topic.words.length, "word", "words"),
    ...(phrases === 0 ? [] : [count(phrases, "way of saying things", "ways of saying things")]),
  ].join(" · ");
}
