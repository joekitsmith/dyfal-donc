import Box from "@mui/material/Box";

import { AppHeader } from "@/components/app-header";
import { BeatRow } from "@/components/beat-row";
import { ErrorCard } from "@/components/error-card";
import { Proverb } from "@/components/proverb";
import { ScreenFrame } from "@/components/screen-frame";

type LessonWaitingProps = {
  /** Set when what the lesson needs could not be loaded. Without it, it is still loading. */
  readonly failure?: { readonly retry: () => void };
};

const BEAT_COUNT = 8;
const SLAB_HEIGHT = 88;

/** The lesson's frame before there is anything to start it with. The start button's place is kept, so nothing moves when it arrives. */
export function LessonWaiting({ failure }: LessonWaitingProps) {
  return (
    <ScreenFrame
      beats={<BeatRow count={BEAT_COUNT} nowIndex={0} />}
      body={
        <>
          <Proverb language="cy" />
          {failure === undefined ? null : (
            <Box sx={{ mt: "20px" }}>
              <ErrorCard
                action={{ label: "Try again", onClick: failure.retry }}
                text="Check your connection, then try again."
                title="We couldn't load this"
              />
            </Box>
          )}
        </>
      }
      controls={<Box sx={{ height: SLAB_HEIGHT }} />}
      english={<Proverb language="en" />}
      header={<AppHeader />}
    />
  );
}
