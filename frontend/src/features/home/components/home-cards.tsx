import Box from "@mui/material/Box";

import { ErrorCard } from "@/components/error-card";
import { SaveProgressPrompt } from "@/features/auth";
import { SessionRecap } from "@/features/learning-session";

import type { HomeCardsContent } from "../types";

import { EverythingMetCard } from "./everything-met-card";
import { HowItGoesCard } from "./how-it-goes-card";

type HomeCardsProps = { readonly cards: HomeCardsContent };

export function HomeCards({ cards }: HomeCardsProps) {
  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: "12px", mt: "20px" }}>
      {cards.error === null ? null : (
        <ErrorCard
          action={{ label: "Try again", onClick: cards.error.retry }}
          text="Check your connection, then try again."
          title="We couldn't load this"
        />
      )}
      {cards.howItGoes ? <HowItGoesCard /> : null}
      {cards.recap === null ? null : <SessionRecap recap={cards.recap} />}
      {cards.everythingMet ? <EverythingMetCard /> : null}
      {cards.guest ? <SaveProgressPrompt /> : null}
    </Box>
  );
}
