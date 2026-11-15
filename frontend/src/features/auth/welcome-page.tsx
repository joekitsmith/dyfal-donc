"use client";

import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";

import { PasskeyFailureAlert } from "./components/passkey-failure-alert";
import { useWelcome } from "./hooks/use-welcome";

export function WelcomePage() {
  const { busy, failure, isLoading, signIn, startGuest, supported } = useWelcome();

  if (isLoading) {
    return <Typography>Loading</Typography>;
  }

  return (
    <Stack component="main" spacing={3} sx={{ maxWidth: 560, mt: { sm: 8, xs: 3 }, mx: "auto", p: 2 }}>
      <Typography component="h1" variant="h4">
        Dyfal donc
      </Typography>
      <Typography>
        A little speaking each day, with each word coming back just before it fades. Start straight away, and add a
        passkey later to keep your progress.
      </Typography>
      <Stack spacing={2}>
        <Button
          disabled={busy}
          onClick={() => {
            startGuest();
          }}
          size="large"
          variant="contained"
        >
          Try it now
        </Button>
        {supported ? (
          <Button
            disabled={busy}
            onClick={() => {
              signIn();
            }}
            size="large"
            variant="outlined"
          >
            Sign in with a passkey
          </Button>
        ) : null}
      </Stack>
      {failure ? <PasskeyFailureAlert failure={failure} /> : null}
    </Stack>
  );
}
