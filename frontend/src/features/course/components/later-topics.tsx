import Typography from "@mui/material/Typography";

import type { TopicProgress } from "../types";

type LaterTopicsProps = { readonly topics: readonly TopicProgress[] };

/** The topics not started yet, by name only. It shows nothing when there are none. */
export function LaterTopics({ topics }: LaterTopicsProps) {
  if (topics.length === 0) {
    return null;
  }

  return (
    <section aria-label="Later in the course">
      <Typography component="h2" variant="h6">
        Later in the course
      </Typography>
      <ul>
        {topics.map((topic) => (
          <li key={topic.name}>{topic.name}</li>
        ))}
      </ul>
    </section>
  );
}
