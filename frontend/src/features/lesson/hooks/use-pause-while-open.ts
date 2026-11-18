import { useEffect, useEffectEvent } from "react";

/**
 * Holds the lesson while a menu or dialog is open, as soon as it is able to: it cannot pause while
 * the next exercise is being fetched, so this waits for that. It never resumes, so closing leaves it
 * paused for the learner to resume.
 */
export function usePauseWhileOpen({
  canPause,
  open,
  pause,
}: {
  readonly canPause: boolean;
  readonly open: boolean;
  readonly pause: () => void;
}) {
  const pauseLesson = useEffectEvent(pause);

  useEffect(() => {
    if (open && canPause) {
      pauseLesson();
    }
  }, [canPause, open]);
}
