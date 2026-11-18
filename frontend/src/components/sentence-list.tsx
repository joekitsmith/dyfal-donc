import Box from "@mui/material/Box";

import type { components } from "@/api/schema";

import { useReplayClip } from "@/hooks/use-replay-clip";

import type { ClipSpeed } from "./sentence-card";

import { SentenceCard } from "./sentence-card";
import { SubHeading } from "./sub-heading";

type Sentence = components["schemas"]["SentenceResponse"];

type SentenceListProps = {
  readonly headingLevel: "h2" | "h3";
  /** Gives each sentence a Report button, which calls this with the sentence. */
  readonly onReport?: (sentence: Sentence) => void;
  readonly sentences: readonly Sentence[];
  readonly title: string;
};

/** Sentence cards under a sub-heading. Only one clip plays at a time, across all the cards. It shows nothing for an empty list. */
export function SentenceList({ headingLevel, onReport, sentences, title }: SentenceListProps) {
  const { failed, play, playing } = useReplayClip();

  if (sentences.length === 0) {
    return null;
  }

  return (
    <section aria-label={title}>
      <SubHeading level={headingLevel}>{title}</SubHeading>
      <Box sx={{ display: "flex", flexDirection: "column", gap: "8px" }}>
        {sentences.map((sentence) => {
          const speedOf = (path: null | string): ClipSpeed | null => {
            if (path === sentence.audio.welsh.standard) {
              return "standard";
            }

            return path === sentence.audio.welsh.slow ? "slow" : null;
          };

          return (
            <SentenceCard
              failedClip={speedOf(failed)}
              key={sentence.id}
              onPlay={(speed) => {
                play(sentence.audio.welsh[speed]);
              }}
              onReport={
                onReport === undefined
                  ? undefined
                  : () => {
                      onReport(sentence);
                    }
              }
              playing={speedOf(playing)}
              sentence={sentence}
            />
          );
        })}
      </Box>
    </section>
  );
}
