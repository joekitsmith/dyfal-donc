import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";

import { TEST_IDS } from "@/config/test-ids";

import { useProgress } from "../api/use-progress";

/** Plain counts of where the learner is. It shows nothing until it has them. */
type ProgressPanelProps = { readonly learnerId: string };

export function ProgressPanel({ learnerId }: ProgressPanelProps) {
  const { data } = useProgress(learnerId);

  if (data === undefined) {
    return null;
  }

  return (
    <Stack aria-label="Progress" component="section" data-testid={TEST_IDS.progress} spacing={0.5}>
      <Typography>
        Introduced: {data.introduced} of {data.course_items} items
      </Typography>
      <Typography>Learning: {data.learning}</Typography>
      <Typography>In review: {data.in_review}</Typography>
      <Typography>Due now: {data.learning_due + data.review_due}</Typography>
    </Stack>
  );
}
