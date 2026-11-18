import Box from "@mui/material/Box";

import type { components } from "@/api/schema";

import { ListCard } from "@/components/list-card";
import { ListRow } from "@/components/list-row";
import { SentenceList } from "@/components/sentence-list";
import { SubHeading } from "@/components/sub-heading";
import { courseItemPath } from "@/config/paths";
import { textStyle } from "@/theme/text-style";

import type { TopicProgress } from "../types";

import { describeTopic } from "../utils/describe-topic";
import { topicTitle } from "../utils/topic-title";

type TopicSectionProps = {
  readonly onReport: (sentence: components["schemas"]["SentenceResponse"]) => void;
  readonly topic: TopicProgress;
};

/** A topic the learner has started, open: what they can say in it, and the words and phrases they have met. */
export function TopicSection({ onReport, topic }: TopicSectionProps) {
  const { phrases, sayable, words } = topic;

  return (
    <section aria-label={topicTitle(topic.name)}>
      <Box sx={{ alignItems: "center", display: "flex", justifyContent: "space-between", mt: "28px" }}>
        <Box component="h2" sx={{ ...textStyle("title"), m: 0 }}>
          {topicTitle(topic.name)}
        </Box>
        {topic.is_current ? (
          <Box
            sx={{ ...textStyle("hint"), alignItems: "center", color: "var(--dd-muted)", display: "flex", gap: "8px" }}
          >
            <Box
              aria-hidden="true"
              sx={{ backgroundColor: "var(--dd-accent)", borderRadius: "2px", height: 20, width: 7 }}
            />
            You&apos;re here
          </Box>
        ) : null}
      </Box>
      <Box sx={{ ...textStyle("body"), color: "var(--dd-muted)", mt: "4px" }}>{describeTopic(topic)}</Box>
      <SentenceList
        headingLevel="h3"
        onReport={onReport}
        sentences={sayable.slice(0, MOST_SENTENCES)}
        title="Things you can say"
      />
      {words.length === 0 ? null : (
        <section aria-label="Words">
          <SubHeading level="h3">Words</SubHeading>
          <ListCard>
            {words.map((word) => (
              <ListRow english={word.english} href={courseItemPath(word.id)} key={word.id} welsh={word.welsh} />
            ))}
          </ListCard>
        </section>
      )}
      {phrases.length === 0 ? null : (
        <section aria-label="Ways of saying things">
          <SubHeading level="h3">Ways of saying things</SubHeading>
          <ListCard>
            {phrases.map((phrase) => (
              <ListRow
                href={courseItemPath(phrase.id)}
                key={phrase.id}
                secondLine={{ size: "body", text: phrase.english }}
                welsh={phrase.welsh}
              />
            ))}
          </ListCard>
        </section>
      )}
    </section>
  );
}

const MOST_SENTENCES = 5;
