import { useEffect, useState } from "react";

import { useOverview } from "../api/use-overview";

const MILLISECONDS_PER_SECOND = 1000;
const MILLISECONDS_PER_MINUTE = 60_000;

/**
 * Seconds since the current learning session began, or null when there is not one yet.
 * The server says when it began and what time it thinks it is, so a wrong clock on this device
 * does not matter. It is read again as each whole minute of the session passes, which is all the
 * clock shows.
 */
export function useSessionClock(): null | number {
  const { data, dataUpdatedAt } = useOverview();
  const [now, setNow] = useState(() => Date.now());
  const session = data?.latest_session ?? null;
  const running = session?.ongoing === true;
  const elapsed =
    data === undefined || !session?.ongoing
      ? null
      : now - (dataUpdatedAt - Date.parse(data.now)) - Date.parse(session.started_at);

  useEffect(() => {
    if (!running || elapsed === null) {
      return;
    }

    const timer = setTimeout(
      () => {
        setNow(Date.now());
      },
      MILLISECONDS_PER_MINUTE - (Math.max(0, elapsed) % MILLISECONDS_PER_MINUTE),
    );

    return () => {
      clearTimeout(timer);
    };
  }, [elapsed, running]);

  return elapsed === null ? null : Math.max(0, Math.floor(elapsed / MILLISECONDS_PER_SECOND));
}
