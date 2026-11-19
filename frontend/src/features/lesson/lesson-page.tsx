"use client";

import { useRequireSession } from "@/features/auth";
import { useSettings } from "@/features/settings";

import { LessonPlayer } from "./components/lesson-player";
import { LessonWaiting } from "./components/lesson-waiting";

export function LessonPage() {
  const { error: sessionError, user } = useRequireSession();
  const settings = useSettings();

  if (sessionError !== null || settings.error !== null) {
    return (
      <LessonWaiting
        failure={{
          retry: () => {
            void settings.refetch();
          },
        }}
      />
    );
  }

  if (user === undefined || settings.data === undefined) {
    return <LessonWaiting />;
  }

  return <LessonPlayer isGuest={user.isGuest} key={user.id} learnerId={user.id} settings={settings.data} />;
}
