"use client";

import Alert from "@mui/material/Alert";
import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import Link from "next/link";

import { ROUTES } from "@/config/paths";
import { useRequireSession } from "@/features/auth";

import { useSettings } from "./api/use-settings";
import { SettingsForm } from "./components/settings-form";

export function SettingsPage() {
  const { error: sessionError, user } = useRequireSession();
  const settings = useSettings();
  const error = sessionError ?? settings.error;

  if (error) {
    return <Alert severity="error">{error.message}</Alert>;
  }

  if (user === undefined || settings.data === undefined) {
    return <Typography>Loading</Typography>;
  }

  return (
    <Stack component="main" spacing={3} sx={{ maxWidth: 560, mt: { sm: 8, xs: 3 }, mx: "auto", p: 2 }}>
      <Button component={Link} href={ROUTES.home} sx={{ alignSelf: "flex-start" }}>
        Back to the lesson
      </Button>
      <Typography component="h1" variant="h4">
        Settings
      </Typography>
      <SettingsForm settings={settings.data} />
    </Stack>
  );
}
