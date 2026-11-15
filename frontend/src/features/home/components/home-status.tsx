import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";

import type { Overview } from "@/features/learning-session";

type HomeStatusProps = { readonly overview: Overview };

/** Where the learner is in the course, and what is waiting for them. */
export function HomeStatus({ overview }: HomeStatusProps) {
  const due = overview.review_due + overview.learning_due;

  return (
    <Stack aria-label="Where you are" component="section" spacing={0.5}>
      <Typography>
        {overview.introduced} of {overview.course_items} items introduced
      </Typography>
      <Typography>{due === 0 ? "Nothing to review right now" : `${due} to review now`}</Typography>
      <Typography>
        {overview.new_words_ready && overview.topic !== null
          ? `New words ready: ${overview.topic}`
          : "You have met every word in the course"}
      </Typography>
    </Stack>
  );
}
