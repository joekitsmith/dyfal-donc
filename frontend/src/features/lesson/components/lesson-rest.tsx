import Box from "@mui/material/Box";

import { AppHeader } from "@/components/app-header";
import { BeatRow } from "@/components/beat-row";
import { Proverb } from "@/components/proverb";
import { ScreenFrame } from "@/components/screen-frame";
import { StartSlab } from "@/components/start-slab";
import { HeadphoneHint, HomeCards, useHome } from "@/features/home";
import { ReportDialog, useReportDialog } from "@/features/problem-report";

import { LessonMenu } from "./lesson-menu";

type LessonRestProps = {
  readonly menu: { readonly isOpen: boolean; readonly onClose: () => void; readonly onOpen: () => void };
  readonly onStart: () => void;
};

const BEAT_COUNT = 8;
const SLAB_HEIGHT = 88;

/** The lesson's frame before it starts, which is Home. Pressing start changes what is in it and not where anything is. */
export function LessonRest({ menu, onStart }: LessonRestProps) {
  const { cards, hint, isLoading, slab } = useHome();
  const report = useReportDialog("general");

  return (
    <>
      <ScreenFrame
        beats={<BeatRow count={BEAT_COUNT} nowIndex={0} />}
        body={
          <>
            <Proverb language="cy" />
            <HomeCards cards={cards} />
          </>
        }
        controls={
          isLoading ? (
            <Box sx={{ height: SLAB_HEIGHT }} />
          ) : (
            <>
              {hint.visible ? <HeadphoneHint /> : null}
              <StartSlab
                keyHint="Space"
                onClick={onStart}
                subtitle={slab.brandNew ? "Start" : "Keep going"}
                title={<span lang="cy">{slab.brandNew ? "Dechrau" : "Dal ati"}</span>}
              />
            </>
          )
        }
        english={<Proverb language="en" />}
        header={<AppHeader menu={<LessonMenu menu={menu} onReport={report.reportNothingInParticular} />} />}
      />
      <ReportDialog {...report.dialog} />
    </>
  );
}
