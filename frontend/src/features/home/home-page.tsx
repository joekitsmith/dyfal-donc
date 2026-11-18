"use client";

import Alert from "@mui/material/Alert";
import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import Link from "next/link";

import { ROUTES } from "@/config/paths";
import { SaveProgressPrompt } from "@/features/auth";
import { SessionRecap } from "@/features/learning-session";
import { ReportDialog } from "@/features/problem-report";

import { HomeStatus } from "./components/home-status";
import { useHome } from "./hooks/use-home";

type HomePageProps = { readonly onStart: () => void };

export function HomePage({ onStart }: HomePageProps) {
  const { error, isLoading, overview, report, user } = useHome();

  // The lesson can still be started when the overview could not be loaded
  if (error) {
    return (
      <Stack component="main" spacing={3} sx={{ maxWidth: 560, mt: { sm: 8, xs: 3 }, mx: "auto", p: 2 }}>
        <Alert severity="error">{error.message}</Alert>
        <Button onClick={onStart} size="large" sx={{ alignSelf: "flex-start" }} variant="contained">
          Start learning
        </Button>
      </Stack>
    );
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
      <Button onClick={onStart} size="large" sx={{ alignSelf: "flex-start" }} variant="contained">
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
      <Button onClick={report.reportNothingInParticular} size="small" sx={{ alignSelf: "flex-start" }}>
        Report a problem
      </Button>
      <ReportDialog {...report.dialog} />
    </Stack>
  );
}
