import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";

import { useLessonPlayer } from "../hooks/use-lesson-player";
import { useThinkTimeMultiplier } from "../hooks/use-think-time-multiplier";
import { ExerciseDisplay } from "./exercise-display";
import { LessonControls } from "./lesson-controls";
import { ThinkTimeSlider } from "./think-time-slider";

export function LessonPlayer({
  learnerId,
  onStartOver,
}: {
  readonly learnerId: string;
  readonly onStartOver: () => void;
}) {
  const [thinkMultiplier, setThinkMultiplier] = useThinkTimeMultiplier();
  const { actions, canMiss, canPause, state } = useLessonPlayer({ learnerId, thinkMultiplier });

  return (
    <Stack spacing={3} sx={{ maxWidth: 560, mx: "auto", p: 2 }}>
      <ExerciseDisplay state={state} />
      <LessonControls actions={actions} canMiss={canMiss} canPause={canPause} state={state} />
      <ThinkTimeSlider onChange={setThinkMultiplier} value={thinkMultiplier} />
      <Button onClick={onStartOver} variant="text">
        Start over
      </Button>
    </Stack>
  );
}
