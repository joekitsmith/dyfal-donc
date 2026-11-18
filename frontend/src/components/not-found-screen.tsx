import { ROUTES } from "@/config/paths";

import { AppHeader } from "./app-header";
import { BeatRow } from "./beat-row";
import { Button } from "./button";
import { LeadText } from "./lead-text";
import { ScreenFrame } from "./screen-frame";

const BEAT_COUNT = 8;

export function NotFoundScreen() {
  return (
    <ScreenFrame
      beats={<BeatRow count={BEAT_COUNT} />}
      body={<LeadText muted>The address may be mistyped, or the page may have moved.</LeadText>}
      controls={
        <Button href={ROUTES.home} variant="primary">
          Go to the start
        </Button>
      }
      english={<h1>{"This page isn't here"}</h1>}
      header={<AppHeader />}
    />
  );
}
