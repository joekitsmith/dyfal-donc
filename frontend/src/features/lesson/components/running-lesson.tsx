import Box from "@mui/material/Box";
import Snackbar from "@mui/material/Snackbar";

import { AppHeader } from "@/components/app-header";
import { BeatRow } from "@/components/beat-row";
import { ScreenFrame } from "@/components/screen-frame";
import { SaveProgressPrompt } from "@/features/auth";
import { SessionClock } from "@/features/learning-session";
import { ReportDialog } from "@/features/problem-report";

import type { LessonActions } from "../hooks/use-lesson-player";
import type { useLessonReport } from "../hooks/use-lesson-report";
import type { useSaveOffer } from "../hooks/use-save-offer";
import type { RunningLessonState } from "../types";

import { useLessonView } from "../hooks/use-lesson-view";
import { hapticTap } from "../utils/haptic-tap";
import { beatRowProps } from "../utils/lesson-view";
import { LessonControls } from "./lesson-controls";
import { LessonMenu } from "./lesson-menu";
import { MissedItSlab } from "./missed-it-slab";
import { SentenceBox } from "./sentence-box";
import { WelshArea } from "./welsh-area";

type RunningLessonProps = {
  readonly actions: LessonActions;
  readonly menu: { readonly isOpen: boolean; readonly onClose: () => void; readonly onOpen: () => void };
  readonly offer: ReturnType<typeof useSaveOffer>;
  readonly report: ReturnType<typeof useLessonReport>;
  readonly state: RunningLessonState;
};

/** The lesson once it has started, in the same frame as when it is at rest. */
export function RunningLesson({ actions, menu, offer, report, state }: RunningLessonProps) {
  const view = useLessonView(state);

  return (
    <>
      <ScreenFrame
        beats={<BeatRow {...beatRowProps(view.beats)} />}
        body={
          <>
            <WelshArea actions={{ onNext: actions.skipWindow, onRetry: actions.retry }} view={view} />
            {offer.prompt.visible ? (
              <Box sx={{ mt: "auto", pt: "12px" }}>
                <SaveProgressPrompt onDismiss={offer.prompt.onDismiss} onSaved={offer.prompt.onSaved} />
              </Box>
            ) : null}
          </>
        }
        controls={
          <>
            <LessonControls actions={actions} controls={view.controls} />
            <MissedItSlab
              onPress={() => {
                if (view.slab === "available") {
                  hapticTap();
                }

                actions.missed();
              }}
              state={view.slab}
            />
          </>
        }
        english={<SentenceBox english={view.english} />}
        header={
          <AppHeader
            clock={<SessionClock />}
            menu={<LessonMenu menu={menu} onReport={report.open} onStop={actions.stop} />}
          />
        }
      />
      <ReportDialog {...report.dialog} />
      <Snackbar
        autoHideDuration={6000}
        message="Saved. You can now sign in from any device with your passkey."
        onClose={offer.confirmation.onClose}
        open={offer.confirmation.open}
      />
    </>
  );
}
