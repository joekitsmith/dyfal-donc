import Accordion from "@mui/material/Accordion";
import AccordionDetails from "@mui/material/AccordionDetails";
import AccordionSummary from "@mui/material/AccordionSummary";
import Chip from "@mui/material/Chip";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";

import { SentenceList } from "@/components/sentence-list";

import type { TopicProgress } from "../types";

import { describeTopic } from "../utils/describe-topic";
import { ItemLinks } from "./item-links";

type TopicAccordionProps = { readonly topic: TopicProgress };

/** A topic the learner has started: what they can say, and the words and phrases they have met. The current topic opens first. */
export function TopicAccordion({ topic }: TopicAccordionProps) {
  return (
    <Accordion
      defaultExpanded={topic.is_current}
      slotProps={{ heading: { component: "h2" }, transition: { unmountOnExit: true } }}
    >
      <AccordionSummary>
        <Stack spacing={0.5}>
          <Stack direction="row" spacing={1} sx={{ alignItems: "center" }}>
            <Typography component="span" variant="h6">
              {topic.name}
            </Typography>
            {topic.is_current ? <Chip label="Current" size="small" /> : null}
          </Stack>
          <Typography color="text.secondary">{describeTopic(topic)}</Typography>
        </Stack>
      </AccordionSummary>
      <AccordionDetails>
        <Stack spacing={2}>
          <SentenceList headingLevel="h3" sentences={topic.sayable} title="Things you can say" />
          <ItemLinks items={topic.words} title="Words" />
          <ItemLinks items={topic.phrases} title="Ways of saying things" />
        </Stack>
      </AccordionDetails>
    </Accordion>
  );
}
