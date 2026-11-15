"use client";

import Alert from "@mui/material/Alert";
import Typography from "@mui/material/Typography";

import { useLearner } from "@/features/learner";

import { Exercise } from "./components/exercise";

export function SmokePage() {
  const { error, isLoading, learnerId } = useLearner();

  if (error) {
    return <Alert severity="error">{error.message}</Alert>;
  }

  if (isLoading || learnerId === undefined) {
    return <Typography>Loading</Typography>;
  }

  return <Exercise learnerId={learnerId} />;
}
