"use client";

import Alert from "@mui/material/Alert";
import Button from "@mui/material/Button";
import Divider from "@mui/material/Divider";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import Link from "next/link";

import { ROUTES } from "@/config/paths";

import { AddPasskeyForm } from "./components/add-passkey-form";
import { DeleteAccountButton } from "./components/delete-account-button";
import { PasskeyList } from "./components/passkey-list";
import { SaveProgressPrompt } from "./components/save-progress-prompt";
import { SignOutButton } from "./components/sign-out-button";
import { useAccount } from "./hooks/use-account";

export function AccountPage() {
  const { deleteAccount, error, isLoading, passkeys, signOut, user } = useAccount();

  if (error) {
    return <Alert severity="error">{error.message}</Alert>;
  }

  if (isLoading || user === undefined) {
    return <Typography>Loading</Typography>;
  }

  return (
    <Stack component="main" spacing={3} sx={{ maxWidth: 560, mt: { sm: 8, xs: 3 }, mx: "auto", p: 2 }}>
      <Button component={Link} href={ROUTES.learn} sx={{ alignSelf: "flex-start" }}>
        Back to the lesson
      </Button>
      <Typography component="h1" variant="h4">
        Account
      </Typography>
      <Typography>{user.isGuest ? "You are using a guest account." : "You are signed in with a passkey."}</Typography>
      {user.isGuest ? <SaveProgressPrompt /> : null}
      <Stack component="section" spacing={1}>
        <Typography component="h2" variant="h6">
          Passkeys
        </Typography>
        <PasskeyList onRemove={passkeys.remove} passkeys={passkeys.items} />
        {passkeys.removeFailed ? <Alert severity="error">The passkey could not be removed. Try again.</Alert> : null}
        {user.isGuest ? null : <AddPasskeyForm />}
      </Stack>
      <Divider />
      <Stack spacing={1} sx={{ alignItems: "flex-start" }}>
        <SignOutButton isGuest={user.isGuest} onSignOut={signOut} />
        <DeleteAccountButton onDelete={deleteAccount} />
      </Stack>
    </Stack>
  );
}
