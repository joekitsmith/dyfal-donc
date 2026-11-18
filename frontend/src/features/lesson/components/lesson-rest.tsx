import Box from "@mui/material/Box";

import { AppHeader } from "@/components/app-header";
import { BeatRow } from "@/components/beat-row";
import { Proverb } from "@/components/proverb";
import { ScreenFrame } from "@/components/screen-frame";
import { StartSlab } from "@/components/start-slab";
import { HeadphoneHint, HomeCards, HomeLinks, useHome } from "@/features/home";

type LessonRestProps = { readonly onStart: () => void };

const BEAT_COUNT = 8;
const SLAB_HEIGHT = 88;

/** The lesson's frame before it starts, which is Home. Pressing start changes what is in it and not where anything is. */
export function LessonRest({ onStart }: LessonRestProps) {
  const { cards, hint, isLoading, slab } = useHome();

  return (
    <ScreenFrame
      beats={<BeatRow count={BEAT_COUNT} nowIndex={0} />}
      body={
        <>
          <Proverb language="cy" />
          <HomeCards cards={cards} />
          <HomeLinks />
        </>
      }
      controls={
        isLoading ? (
          <Box sx={{ height: SLAB_HEIGHT }} />
        ) : (
          <>
            {hint.visible ? <HeadphoneHint /> : null}
            <StartSlab
              onClick={onStart}
              subtitle={slab.brandNew ? "Start" : "Keep going"}
              title={<span lang="cy">{slab.brandNew ? "Dechrau" : "Dal ati"}</span>}
            />
          </>
        )
      }
      english={<Proverb language="en" />}
      header={<AppHeader />}
    />
  );
}
