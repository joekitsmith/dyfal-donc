import { useHeadphoneVisit } from "@/features/home";
import { useDisclosure } from "@/hooks/use-disclosure";

import type { LessonSettings } from "../types";

import { useLessonPlayer } from "../hooks/use-lesson-player";
import { useLessonReport } from "../hooks/use-lesson-report";
import { usePauseWhileOpen } from "../hooks/use-pause-while-open";
import { useSaveOffer } from "../hooks/use-save-offer";
import { LessonRest } from "./lesson-rest";
import { RunningLesson } from "./running-lesson";

type LessonPlayerProps = {
  readonly isGuest: boolean;
  readonly learnerId: string;
  readonly settings: LessonSettings;
};

export function LessonPlayer({ isGuest, learnerId, settings }: LessonPlayerProps) {
  const { actions, canPause, readThink, recent, state } = useLessonPlayer({ learnerId, settings });
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
    <RunningLesson
      actions={actions}
      menu={menuProps}
      offer={offer}
      readThink={readThink}
      report={report}
      state={state}
    />
  );
}
