import { useEffect, useState } from "react";

import { useOverview } from "../api/use-overview";

const TICK_MILLISECONDS = 1000;
const MILLISECONDS_PER_SECOND = 1000;

/**
 * Seconds since the current learning session began, or null when there is not one yet.
 * The server says when it began and what time it thinks it is, so a wrong clock on this device
 * does not matter.
 */
export function useSessionClock(): null | number {
  const { data, dataUpdatedAt } = useOverview();
  const [now, setNow] = useState(() => Date.now());
  const session = data?.latest_session ?? null;
  const running = session?.ongoing === true;

  useEffect(() => {
    if (!running) {
      return;
    }

    const timer = setInterval(() => {
      setNow(Date.now());
    }, TICK_MILLISECONDS);

    return () => {
      clearInterval(timer);
    };
  }, [running]);

  if (data === undefined || !session?.ongoing) {
    return null;
  }

  const behindServer = dataUpdatedAt - Date.parse(data.now);
  const elapsed = now - behindServer - Date.parse(session.started_at);

  return Math.max(0, Math.floor(elapsed / MILLISECONDS_PER_SECOND));
}
