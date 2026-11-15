"use client";

import Alert from "@mui/material/Alert";
import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import Link from "next/link";

import { ROUTES } from "@/config/paths";

import { ItemList } from "./components/item-list";
import { MissedExerciseList } from "./components/missed-exercise-list";
import { useSummaryPage } from "./hooks/use-summary-page";
import { formatDuration } from "./utils/format-time";

type SummaryPageProps = { readonly sessionId: number };

export function SummaryPage({ sessionId }: SummaryPageProps) {
  const { error, isLoading, notFound, summary } = useSummaryPage(sessionId);

  if (notFound) {
    return (
      <Stack component="main" spacing={2} sx={{ maxWidth: 560, mt: { sm: 8, xs: 3 }, mx: "auto", p: 2 }}>
        <Typography>That learning session does not exist.</Typography>
        <Button component={Link} href={ROUTES.home} sx={{ alignSelf: "flex-start" }}>
          Back to home
        </Button>
      </Stack>
    );
  }

  if (error) {
    return <Alert severity="error">{error.message}</Alert>;
  }

  if (isLoading || summary === undefined) {
    return <Typography>Loading</Typography>;
  }

  const exercises = summary.exercises_completed === 1 ? "1 exercise" : `${summary.exercises_completed} exercises`;

  return (
    <Stack component="main" spacing={3} sx={{ maxWidth: 560, mt: { sm: 8, xs: 3 }, mx: "auto", p: 2 }}>
      <Button component={Link} href={ROUTES.home} sx={{ alignSelf: "flex-start" }}>
        Back to home
      </Button>
      <Typography component="h1" variant="h4">
        Learning session
      </Typography>
      <Typography>
        {exercises}, {formatDuration(summary.duration_seconds)}
        {summary.ongoing ? ", still going" : ""}
      </Typography>
      {summary.items_reviewed > 0 ? (
        <Typography>
          Reviewed {summary.items_reviewed} {summary.items_reviewed === 1 ? "word" : "words"} you already knew
        </Typography>
      ) : null}
      <ItemList items={summary.items_introduced} title="New words" />
      <ItemList items={summary.items_lapsed} title="Words that slipped" />
      <MissedExerciseList exercises={summary.missed_exercises} />
      <Button component={Link} href={ROUTES.learn} sx={{ alignSelf: "flex-start" }} variant="contained">
        {summary.ongoing ? "Keep going" : "Start another"}
      </Button>
    </Stack>
  );
}
