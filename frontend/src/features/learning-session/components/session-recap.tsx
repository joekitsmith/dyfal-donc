import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import Link from "next/link";

import { learningSessionPath } from "@/config/paths";

import type { SessionRecap as Recap } from "../types";

import { formatDuration } from "../utils/format-time";
import { ItemList } from "./item-list";

type SessionRecapProps = { readonly recap: Recap };

/** A short account of a learning session: how long, how many exercises, and the new words. */
export function SessionRecap({ recap }: SessionRecapProps) {
  const exercises = recap.exercises_completed === 1 ? "1 exercise" : `${recap.exercises_completed} exercises`;

  return (
    <Card aria-label="Latest session" component="section" variant="outlined">
      <CardContent>
        <Stack spacing={1}>
          <Typography component="h2" variant="h6">
            {recap.ongoing ? "This session so far" : "Last time"}
          </Typography>
          <Typography>
            {exercises}, {formatDuration(recap.duration_seconds)}
          </Typography>
          <ItemList items={recap.items_introduced} title="New words" />
          <Button component={Link} href={learningSessionPath(recap.id)} sx={{ alignSelf: "flex-start" }}>
            See details
          </Button>
        </Stack>
      </CardContent>
    </Card>
  );
}
