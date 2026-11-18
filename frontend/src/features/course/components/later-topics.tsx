import Box from "@mui/material/Box";

import { SubHeading } from "@/components/sub-heading";
import { textStyle } from "@/theme/text-style";

import type { TopicProgress } from "../types";

import { topicTitle } from "../utils/topic-title";

type LaterTopicsProps = { readonly topics: readonly TopicProgress[] };

/** The topics not started yet, by name only. It shows nothing when there are none. */
export function LaterTopics({ topics }: LaterTopicsProps) {
  if (topics.length === 0) {
    return null;
  }

  return (
    <section aria-label="Later in the course">
      <SubHeading level="h2">Later in the course</SubHeading>
      <Box sx={{ ...textStyle("label"), color: "var(--dd-muted)", fontWeight: 400, lineHeight: 1.7, m: 0 }}>
        {topics.map((topic) => topicTitle(topic.name)).join(" · ")}
      </Box>
    </section>
  );
}
