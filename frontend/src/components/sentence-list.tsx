import Alert from "@mui/material/Alert";
import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";

import type { components } from "@/api/schema";

import { useReplayClip } from "@/hooks/use-replay-clip";

type Sentence = components["schemas"]["SentenceResponse"];

type SentenceListProps = {
  readonly headingLevel: "h2" | "h3";
  /** Gives each sentence a Report button, which calls this with the sentence. */
  readonly onReport?: (sentence: Sentence) => void;
  readonly sentences: readonly Sentence[];
  readonly title: string;
};

/** Sentences in both languages, each with the Welsh to play at either pace. It shows nothing for an empty list. */
export function SentenceList({ headingLevel, onReport, sentences, title }: SentenceListProps) {
  const { failed, play } = useReplayClip();

  if (sentences.length === 0) {
    return null;
  }

  return (
    <Stack aria-label={title} component="section" spacing={1}>
      <Typography component={headingLevel} variant="h6">
        {title}
      </Typography>
      {sentences.map((sentence) => (
        <Stack key={sentence.id} spacing={0.5}>
          <Typography>{sentence.english}</Typography>
          <Typography>{sentence.welsh}</Typography>
          <Stack direction="row" spacing={1}>
            <Button
              aria-label={`Play ${sentence.welsh}`}
              onClick={() => {
                play(sentence.audio.welsh.standard);
              }}
              variant="outlined"
            >
              Play
            </Button>
            <Button
              aria-label={`Play ${sentence.welsh} slowly`}
              onClick={() => {
                play(sentence.audio.welsh.slow);
              }}
              variant="outlined"
            >
              Play slowly
            </Button>
            {onReport === undefined ? null : (
              <Button
                aria-label={`Report ${sentence.welsh}`}
                onClick={() => {
                  onReport(sentence);
                }}
                size="small"
              >
                Report
              </Button>
            )}
          </Stack>
        </Stack>
      ))}
      {failed ? <Alert severity="error">The audio could not be played</Alert> : null}
    </Stack>
  );
}
