import { ROUTES } from "@/config/paths";

import { AppHeader } from "./app-header";
import { BeatRow } from "./beat-row";
import { Button } from "./button";
import { LeadText } from "./lead-text";
import { ScreenFrame } from "./screen-frame";

type FailureScreenProps = { readonly onRetry: () => void };

const BEAT_COUNT = 8;

export function FailureScreen({ onRetry }: FailureScreenProps) {
  return (
    <ScreenFrame
      beats={<BeatRow count={BEAT_COUNT} />}
      body={<LeadText muted>{"It's a problem on our side, not something you did. Your progress is safe."}</LeadText>}
      controls={
        <>
          <Button onClick={onRetry} variant="quiet">
            Try again
          </Button>
          <Button href={ROUTES.home} variant="primary">
            Go to the start
          </Button>
        </>
      }
      english={<h1>Something went wrong</h1>}
      header={<AppHeader />}
    />
  );
}
