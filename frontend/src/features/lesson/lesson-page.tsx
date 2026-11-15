"use client";

import Alert from "@mui/material/Alert";
import Typography from "@mui/material/Typography";

import { useRequireSession } from "@/features/auth";

import { LessonPlayer } from "./components/lesson-player";

export function LessonPage() {
  const { error, user } = useRequireSession();

  if (error) {
    return <Alert severity="error">{error.message}</Alert>;
  }

  if (user === undefined) {
    return <Typography>Loading</Typography>;
  }

  return <LessonPlayer isGuest={user.isGuest} key={user.id} learnerId={user.id} />;
}
