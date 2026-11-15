"use client";

import Typography from "@mui/material/Typography";

import { useHomeRedirect } from "@/features/auth";

/** For now the home screen only sends people on: to the lesson, or the welcome screen. */
export function HomePage() {
  useHomeRedirect();

  return <Typography>Loading</Typography>;
}
