import type { TopicProgress } from "../types";

function count(amount: number, singular: string, plural: string): string {
  return `${amount} ${amount === 1 ? singular : plural}`;
}

/** What the learner has met in the topic, such as "12 words · 4 ways of saying things · 42 exercises answered". */
export function describeTopic(topic: TopicProgress): string {
  return [
    count(topic.words.length, "word", "words"),
    count(topic.phrases.length, "way of saying things", "ways of saying things"),
    `${count(topic.exercises_answered, "exercise", "exercises")} answered`,
  ].join(" · ");
}
