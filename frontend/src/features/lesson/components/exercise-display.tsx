import Typography from "@mui/material/Typography";

import type { LessonState } from "../types";

import { isExerciseState } from "../stores/lesson-reducer";

const PHASE_LABELS: Readonly<Record<LessonState["phase"], string>> = {
  awaiting_outcome: "Did you get it?",
  error: "Something went wrong",
  idle: "Ready when you are",
  loading: "Loading",
  nothing_eligible: "Nothing to do right now",
  playing_english: "Listen",
  playing_welsh: "Listen",
  playing_welsh_slow: "Listen again, more slowly",
  preparing: "Loading",
  submitting: "Saving",
  thinking: "Say it in Welsh",
  waiting_for_clip: "Loading the Welsh",
};

export function ExerciseDisplay({ state }: { readonly state: LessonState }) {
  return (
    <>
      <Typography aria-live="polite" color="text.secondary">
        {PHASE_LABELS[state.phase]}
        {isExerciseState(state) && state.paused ? " (paused)" : ""}
      </Typography>
      {isExerciseState(state) ? (
        <>
          <Typography variant="h5">{state.exercise.english}</Typography>
          {state.revealed ? <Typography variant="h5">{state.exercise.welsh}</Typography> : null}
          {state.missed ? <Typography color="warning.main">Marked as missed</Typography> : null}
        </>
      ) : null}
      {state.phase === "nothing_eligible" ? <Typography>{state.reason}</Typography> : null}
      {state.phase === "error" ? <Typography color="error">{state.message}</Typography> : null}
    </>
  );
}
