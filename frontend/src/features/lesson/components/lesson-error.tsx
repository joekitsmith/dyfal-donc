import { ErrorCard } from "@/components/error-card";
import { ROUTES } from "@/config/paths";

import type { LessonViewError } from "../utils/lesson-view";

type LessonErrorProps = {
  readonly error: LessonViewError;
  readonly onRetry: () => void;
};

export function LessonError({ error, onRetry }: LessonErrorProps) {
  const { action, text, title } = error;

  return (
    <ErrorCard
      action={
        action === null
          ? undefined
          : action === "account"
            ? { href: ROUTES.account, label: "Go to account" }
            : { label: "Try again", onClick: onRetry }
      }
      text={text}
      title={title}
    />
  );
}
