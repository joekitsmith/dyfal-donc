/** The topic ids are internal. The first topic, which everything else builds on, is called what a learner would call it. */
const TITLES: Readonly<Record<string, string>> = { spine: "Everyday talk" };

/** The English name a learner sees for a topic, such as "Everyday talk" or "Food". */
export function topicTitle(name: string): string {
  return TITLES[name] ?? `${name.charAt(0).toUpperCase()}${name.slice(1)}`;
}
