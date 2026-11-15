import type { ReportSubject } from "@/features/problem-report";

import { useDisclosure } from "@/hooks/use-disclosure";

import type { LessonExercise, LessonState } from "../types";

import { isExerciseState } from "../stores/lesson-reducer";
import { exerciseSubject } from "../utils/exercise-subject";

/**
 * Reporting from the lesson: the button pauses it and opens the dialog about the sentences just heard.
 * The one on screen is only offered once its Welsh shows, so reporting never gives it away. The lesson
 * stays paused afterwards, and the learner resumes when ready.
 */
export function useLessonReport({
  canPause,
  pause,
  recent,
  state,
}: {
  readonly canPause: boolean;
  readonly pause: () => void;
  readonly recent: readonly LessonExercise[];
  readonly state: LessonState;
}) {
  const { close, isOpen, open } = useDisclosure();
  const current = isExerciseState(state) ? state : null;
  const subjects: readonly ReportSubject[] = recent
    .filter((exercise) => current === null || current.revealed || exercise.selectionId !== current.exercise.selectionId)
    .map(exerciseSubject);

  return {
    button: {
      disabled: !canPause,
      onClick: () => {
        pause();
        open();
      },
    },
    dialog: { allowNone: true, onClose: close, open: isOpen, source: "lesson", subjects } as const,
  };
}
