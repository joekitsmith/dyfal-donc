import Box from "@mui/material/Box";

import { Button } from "@/components/button";
import { PauseIcon } from "@/components/icons/pause-icon";
import { PlayIcon } from "@/components/icons/play-icon";
import { ReplayIcon } from "@/components/icons/replay-icon";

import type { LessonActions } from "../hooks/use-lesson-player";
import type { LessonView } from "../utils/lesson-view";

type LessonControlsProps = {
  readonly actions: Pick<LessonActions, "replay" | "togglePause">;
  readonly controls: LessonView["controls"];
};

/** Presses that cannot do anything yet are ignored by the lesson, whatever these look like. */
export function LessonControls({ actions, controls }: LessonControlsProps) {
  const unavailable = controls.look === "unavailable";

  return (
    <Box sx={{ display: "flex", gap: "12px" }}>
      <Box sx={{ flex: 1 }}>
        <Button onClick={actions.replay} unavailable={unavailable} variant="quiet">
          <ReplayIcon size={20} />
          Replay
        </Button>
      </Box>
      <Box sx={{ flex: 1 }}>
        {controls.pause === "resume" ? (
          <Button onClick={actions.togglePause} unavailable={unavailable} variant="primary">
            <PlayIcon size={20} />
            Resume
          </Button>
        ) : (
          <Button onClick={actions.togglePause} unavailable={unavailable} variant="quiet">
            <PauseIcon size={20} />
            Pause
          </Button>
        )}
      </Box>
    </Box>
  );
}
