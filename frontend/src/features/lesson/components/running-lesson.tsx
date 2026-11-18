import Box from "@mui/material/Box";

import { AppHeader } from "@/components/app-header";
import { BeatRow } from "@/components/beat-row";
import { ScreenFrame } from "@/components/screen-frame";
import { PasskeyAddedNotice, SaveProgressPrompt } from "@/features/auth";
import { SessionClock } from "@/features/learning-session";
import { ReportDialog } from "@/features/problem-report";

import type { LessonActions } from "../hooks/use-lesson-player";
import type { useLessonReport } from "../hooks/use-lesson-report";
import type { useSaveOffer } from "../hooks/use-save-offer";
import type { RunningLessonState } from "../types";

import { useBeatIndex } from "../hooks/use-beat-index";
import { useFittedSize } from "../hooks/use-fitted-size";
import { useLessonView } from "../hooks/use-lesson-view";
import { type ThinkWindow } from "../utils/beats";
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
  /** Where the audio is in the think time, read on each frame. */
  readonly readThink: () => null | ThinkWindow;
  readonly report: ReturnType<typeof useLessonReport>;
  readonly state: RunningLessonState;
};

/** The lesson once it has started, in the same frame as when it is at rest. */
export function RunningLesson({ actions, menu, offer, readThink, report, state }: RunningLessonProps) {
  const view = useLessonView(state);
  const fit = useFittedSize();
  const beatIndex = useBeatIndex({
    count: view.beats.count,
    counting: view.beats.mode === "counting" && !view.paused,
    read: readThink,
    run: view.beats.run,
  });

  return (
    <>
      <ScreenFrame
        beats={<BeatRow {...beatRowProps(view.beats, beatIndex)} />}
        body={
          <>
            <WelshArea actions={{ onNext: actions.skipWindow, onRetry: actions.retry }} fit={fit.welsh} view={view} />
            {offer.prompt.visible || offer.confirmation.visible ? (
              <Box sx={{ mt: "auto", py: "12px" }}>
                {offer.prompt.visible ? (
                  <SaveProgressPrompt onDismiss={offer.prompt.onDismiss} onSaved={offer.prompt.onSaved} />
                ) : (
                  <PasskeyAddedNotice />
                )}
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
        english={<SentenceBox english={view.english} fit={fit.english} />}
        header={
          <AppHeader
            clock={<SessionClock />}
            menu={<LessonMenu menu={menu} onReport={report.open} onStop={actions.stop} />}
          />
        }
      />
      <ReportDialog {...report.dialog} />
    </>
  );
}
