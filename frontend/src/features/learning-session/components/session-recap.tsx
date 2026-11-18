import Box from "@mui/material/Box";

import { TextLink } from "@/components/text-link";
import { learningSessionPath, ROUTES } from "@/config/paths";
import { textStyle } from "@/theme/text-style";

import type { SessionRecap as Recap } from "../types";

import { formatClock } from "../utils/format-time";
import { RecapWords } from "./recap-words";

type SessionRecapProps = { readonly recap: Recap };

/** What the last session was: how much, how long, and the new words, with a way into each. */
export function SessionRecap({ recap }: SessionRecapProps) {
  const sentences = recap.exercises_completed === 1 ? "1 sentence" : `${recap.exercises_completed} sentences`;

  return (
    <Box
      aria-label="Latest session"
      component="section"
      sx={{ backgroundColor: "var(--dd-surface)", borderRadius: "10px", p: "14px 18px 4px" }}
    >
      <Box sx={{ ...textStyle("body"), color: "var(--dd-muted)" }}>
        {recap.ongoing ? "This session so far" : "Last time"} · {sentences}, {formatClock(recap.duration_seconds)}
      </Box>
      <RecapWords items={recap.items_introduced} sessionId={recap.id} />
      <Box sx={{ display: "flex", flexWrap: "wrap", gap: "24px" }}>
        <TextLink href={learningSessionPath(recap.id)} inline medium>
          Look back
        </TextLink>
        <TextLink href={ROUTES.course} inline medium>
          {"Everything you've met"}
        </TextLink>
      </Box>
    </Box>
  );
}
