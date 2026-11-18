import Snackbar from "@mui/material/Snackbar";
import Stack from "@mui/material/Stack";

import { AppHeader } from "@/components/app-header";
import { SaveProgressPrompt } from "@/features/auth";
import { useHeadphoneVisit } from "@/features/home";
import { SessionClock } from "@/features/learning-session";
import { ReportDialog } from "@/features/problem-report";
import { ProgressPanel } from "@/features/progress";
import { useDisclosure } from "@/hooks/use-disclosure";

import type { LessonSettings } from "../types";

import { useLessonPlayer } from "../hooks/use-lesson-player";
import { useLessonReport } from "../hooks/use-lesson-report";
import { usePauseWhileOpen } from "../hooks/use-pause-while-open";
import { useSaveOffer } from "../hooks/use-save-offer";
import { ExerciseDisplay } from "./exercise-display";
import { LessonControls } from "./lesson-controls";
import { LessonMenu } from "./lesson-menu";
import { LessonRest } from "./lesson-rest";
import { ThinkProgress } from "./think-progress";

type LessonPlayerProps = {
  readonly isGuest: boolean;
  readonly learnerId: string;
  readonly settings: LessonSettings;
};

export function LessonPlayer({ isGuest, learnerId, settings }: LessonPlayerProps) {
  const { actions, canMiss, canPause, recent, state } = useLessonPlayer({ learnerId, settings });
  const report = useLessonReport({ recent, state });
  const offer = useSaveOffer({ isGuest, learnerId });
  const menu = useDisclosure();
  const menuProps = { isOpen: menu.isOpen, onClose: menu.close, onOpen: menu.open };

  usePauseWhileOpen({ canPause, open: menu.isOpen || report.dialog.open, pause: actions.pause });

  useHeadphoneVisit();

  if (state.phase === "idle") {
    return <LessonRest menu={menuProps} onStart={actions.start} />;
  }

  return (
    <Stack component="main" spacing={3} sx={{ maxWidth: 560, mt: { sm: 8, xs: 3 }, mx: "auto", p: 2 }}>
      {offer.prompt.visible ? (
        <SaveProgressPrompt onDismiss={offer.prompt.onDismiss} onSaved={offer.prompt.onSaved} />
      ) : null}
      <AppHeader
        clock={<SessionClock />}
        menu={<LessonMenu menu={menuProps} onReport={report.open} onStop={actions.stop} />}
      />
      <ExerciseDisplay state={state} />
      <ThinkProgress multiplier={settings.thinkTimeMultiplier} state={state} />
      <LessonControls actions={actions} canMiss={canMiss} canPause={canPause} state={state} />
      <ProgressPanel learnerId={learnerId} />
      <ReportDialog {...report.dialog} />
      <Snackbar
        autoHideDuration={6000}
        message="Saved. You can now sign in from any device with your passkey."
        onClose={offer.confirmation.onClose}
        open={offer.confirmation.open}
      />
    </Stack>
  );
}
