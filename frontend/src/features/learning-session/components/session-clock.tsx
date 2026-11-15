import Typography from "@mui/material/Typography";

import { useSessionClock } from "../hooks/use-session-clock";
import { formatClock } from "../utils/format-time";

/** How long this learning session has been going. It shows nothing until the first answer. */
export function SessionClock() {
  const seconds = useSessionClock();

  if (seconds === null) {
    return null;
  }

  return (
    <Typography aria-label="Time in this session" color="text.secondary" role="timer">
      {formatClock(seconds)}
    </Typography>
  );
}
