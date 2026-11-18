import Box from "@mui/material/Box";

import { TEST_IDS } from "@/config/test-ids";
import { textStyle } from "@/theme/text-style";

import { useSessionClock } from "../hooks/use-session-clock";
import { formatClock } from "../utils/format-time";

/** How long this learning session has been going. It shows nothing until the first answer, and is read out in the summary instead. */
export function SessionClock() {
  const seconds = useSessionClock();

  if (seconds === null) {
    return null;
  }

  return (
    <Box aria-hidden="true" data-testid={TEST_IDS.sessionClock} sx={{ ...textStyle("body"), color: "var(--dd-muted)" }}>
      {formatClock(seconds)}
    </Box>
  );
}
