import Button from "@mui/material/Button";
import Snackbar from "@mui/material/Snackbar";
import Stack from "@mui/material/Stack";
import Link from "next/link";

import { ROUTES } from "@/config/paths";
import { SaveProgressPrompt } from "@/features/auth";
import { ProgressPanel } from "@/features/progress";

import { useLessonPlayer } from "../hooks/use-lesson-player";
import { useSaveOffer } from "../hooks/use-save-offer";
import { useThinkTimeMultiplier } from "../hooks/use-think-time-multiplier";
import { ExerciseDisplay } from "./exercise-display";
import { LessonControls } from "./lesson-controls";
import { ThinkProgress } from "./think-progress";
import { ThinkTimeSlider } from "./think-time-slider";

export function LessonPlayer({ isGuest, learnerId }: { readonly isGuest: boolean; readonly learnerId: string }) {
  const [thinkMultiplier, setThinkMultiplier] = useThinkTimeMultiplier();
  const { actions, canMiss, canPause, state } = useLessonPlayer({ learnerId, thinkMultiplier });
  const offer = useSaveOffer({ isGuest, learnerId });

  return (
    <Stack component="main" spacing={3} sx={{ maxWidth: 560, mt: { sm: 8, xs: 3 }, mx: "auto", p: 2 }}>
      {offer.offered ? <SaveProgressPrompt onDismiss={offer.dismiss} onSaved={offer.markSaved} /> : null}
      <ExerciseDisplay state={state} />
      <ThinkProgress multiplier={thinkMultiplier} state={state} />
      <LessonControls actions={actions} canMiss={canMiss} canPause={canPause} state={state} />
      <ThinkTimeSlider onChange={setThinkMultiplier} value={thinkMultiplier} />
      <ProgressPanel learnerId={learnerId} />
      <Button component={Link} href={ROUTES.account} sx={{ alignSelf: "flex-start" }}>
        Account
      </Button>
      <Snackbar
        autoHideDuration={6000}
        message="Saved. You can now sign in from any device with your passkey."
        onClose={offer.closeSaved}
        open={offer.saved}
      />
    </Stack>
  );
}
