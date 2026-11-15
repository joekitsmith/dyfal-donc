"use client";

import Alert from "@mui/material/Alert";
import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import Link from "next/link";

import { ROUTES } from "@/config/paths";
import { SaveProgressPrompt } from "@/features/auth";
import { SessionRecap } from "@/features/learning-session";

import { HomeStatus } from "./components/home-status";
import { useHome } from "./hooks/use-home";

export function HomePage() {
  const { error, isLoading, overview, user } = useHome();

  if (error) {
    return <Alert severity="error">{error.message}</Alert>;
  }

  if (isLoading || overview === undefined || user === undefined) {
    return <Typography>Loading</Typography>;
  }

  const recap = overview.latest_session;

  return (
    <Stack component="main" spacing={3} sx={{ maxWidth: 560, mt: { sm: 8, xs: 3 }, mx: "auto", p: 2 }}>
      <Typography component="h1" variant="h4">
        Dyfal donc
      </Typography>
      {recap === null ? null : <SessionRecap recap={recap} />}
      <HomeStatus overview={overview} />
      <Button component={Link} href={ROUTES.learn} size="large" sx={{ alignSelf: "flex-start" }} variant="contained">
        {recap?.ongoing === true ? "Continue learning" : "Start learning"}
      </Button>
      {user.isGuest && recap !== null ? <SaveProgressPrompt /> : null}
      <Stack direction="row" spacing={1}>
        <Button component={Link} href={ROUTES.course}>
          Course
        </Button>
        <Button component={Link} href={ROUTES.settings}>
          Settings
        </Button>
        <Button component={Link} href={ROUTES.account}>
          Account
        </Button>
      </Stack>
    </Stack>
  );
}
