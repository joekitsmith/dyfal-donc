"use client";

import Alert from "@mui/material/Alert";
import Typography from "@mui/material/Typography";

import { useLearner } from "@/features/learner";

import { LessonPlayer } from "./components/lesson-player";

export function LessonPage() {
  const { error, isLoading, learnerId, startOver } = useLearner();

  if (error) {
    return <Alert severity="error">{error.message}</Alert>;
  }

  if (isLoading || learnerId === undefined) {
    return <Typography>Loading</Typography>;
  }

  return (
    <LessonPlayer
      key={learnerId}
      learnerId={learnerId}
      onStartOver={() => {
        startOver();
      }}
    />
  );
}
