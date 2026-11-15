import Button from "@mui/material/Button";
import Snackbar from "@mui/material/Snackbar";
import Stack from "@mui/material/Stack";
import Link from "next/link";

import { ROUTES } from "@/config/paths";
import { SaveProgressPrompt } from "@/features/auth";
import { ProgressPanel } from "@/features/progress";

import type { LessonSettings } from "../types";

import { useLessonPlayer } from "../hooks/use-lesson-player";
import { useSaveOffer } from "../hooks/use-save-offer";
import { ExerciseDisplay } from "./exercise-display";
import { LessonControls } from "./lesson-controls";
import { ThinkProgress } from "./think-progress";

type LessonPlayerProps = {
  readonly isGuest: boolean;
  readonly learnerId: string;
  readonly settings: LessonSettings;
};

export function LessonPlayer({ isGuest, learnerId, settings }: LessonPlayerProps) {
  const { actions, canMiss, canPause, state } = useLessonPlayer({ learnerId, settings });
  const offer = useSaveOffer({ isGuest, learnerId });

  return (
    <Stack component="main" spacing={3} sx={{ maxWidth: 560, mt: { sm: 8, xs: 3 }, mx: "auto", p: 2 }}>
      {offer.prompt.visible ? (
        <SaveProgressPrompt onDismiss={offer.prompt.onDismiss} onSaved={offer.prompt.onSaved} />
      ) : null}
      <ExerciseDisplay state={state} />
      <ThinkProgress multiplier={settings.thinkTimeMultiplier} state={state} />
      <LessonControls actions={actions} canMiss={canMiss} canPause={canPause} state={state} />
      <ProgressPanel learnerId={learnerId} />
      <Stack direction="row" spacing={1}>
        <Button component={Link} href={ROUTES.account}>
          Account
        </Button>
        <Button component={Link} href={ROUTES.settings}>
          Settings
        </Button>
      </Stack>
      <Snackbar
        autoHideDuration={6000}
        message="Saved. You can now sign in from any device with your passkey."
        onClose={offer.confirmation.onClose}
        open={offer.confirmation.open}
      />
    </Stack>
  );
}
