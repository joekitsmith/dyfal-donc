"use client";

import Alert from "@mui/material/Alert";
import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import Link from "next/link";

import { ROUTES } from "@/config/paths";

import { AddPasskeyForm } from "./components/add-passkey-form";
import { useRecover } from "./hooks/use-recover";

export function RecoverPage() {
  const { failure, field, isLoading, isSigningIn, onSubmit, recovered } = useRecover();

  if (isLoading) {
    return <Typography>Loading</Typography>;
  }

  return (
    <Stack component="main" spacing={3} sx={{ maxWidth: 560, mt: { sm: 8, xs: 3 }, mx: "auto", p: 2 }}>
      <Typography component="h1" variant="h4">
        Recover your account
      </Typography>
      {recovered ? (
        <Stack spacing={2}>
          <Alert severity="success">
            You are signed in. Add a new passkey now, so you do not need another code next time.
          </Alert>
          <AddPasskeyForm submitLabel="Add a new passkey" />
          <Button component={Link} href={ROUTES.learn}>
            Continue to the lesson
          </Button>
        </Stack>
      ) : (
        <Stack
          component="form"
          noValidate
          onSubmit={(event) => {
            void onSubmit(event);
          }}
          spacing={2}
        >
          <Typography>Lost your passkey? Enter one of the recovery codes you saved. Each works once.</Typography>
          <TextField
            autoComplete="off"
            error={field.error}
            helperText={field.helperText}
            label="Recovery code"
            {...field.register}
          />
          <Button disabled={isSigningIn} size="large" type="submit" variant="contained">
            Sign in
          </Button>
          {failure ? <Alert severity="error">{failure}</Alert> : null}
          <Button component={Link} href={ROUTES.welcome}>
            Back
          </Button>
        </Stack>
      )}
    </Stack>
  );
}
