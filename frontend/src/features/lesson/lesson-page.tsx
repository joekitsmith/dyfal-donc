"use client";

import Alert from "@mui/material/Alert";
import Typography from "@mui/material/Typography";

import { useRequireSession } from "@/features/auth";
import { useSettings } from "@/features/settings";

import { LessonPlayer } from "./components/lesson-player";

export function LessonPage() {
  const { error: sessionError, user } = useRequireSession();
  const settings = useSettings();
  const error = sessionError ?? settings.error;

  if (error) {
    return <Alert severity="error">{error.message}</Alert>;
  }

  if (user === undefined || settings.data === undefined) {
    return <Typography>Loading</Typography>;
  }

  return <LessonPlayer isGuest={user.isGuest} key={user.id} learnerId={user.id} settings={settings.data} />;
}
