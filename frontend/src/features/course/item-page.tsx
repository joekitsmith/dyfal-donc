"use client";

import Alert from "@mui/material/Alert";
import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import Link from "next/link";

import { SentenceList } from "@/components/sentence-list";
import { ROUTES } from "@/config/paths";

import { ItemDetails } from "./components/item-details";
import { useItemPage } from "./hooks/use-item-page";

type ItemPageProps = { readonly itemId: string };

export function ItemPage({ itemId }: ItemPageProps) {
  const { error, isLoading, item, notFound, playback } = useItemPage(itemId);

  if (notFound) {
    return (
      <Stack component="main" spacing={2} sx={{ maxWidth: 560, mt: { sm: 8, xs: 3 }, mx: "auto", p: 2 }}>
        <Typography>We could not find that word.</Typography>
        <Button component={Link} href={ROUTES.course} sx={{ alignSelf: "flex-start" }}>
          Back to the course
        </Button>
      </Stack>
    );
  }

  if (error) {
    return <Alert severity="error">{error.message}</Alert>;
  }

  if (isLoading || item === undefined) {
    return <Typography>Loading</Typography>;
  }

  return (
    <Stack component="main" spacing={3} sx={{ maxWidth: 560, mt: { sm: 8, xs: 3 }, mx: "auto", p: 2 }}>
      <Button component={Link} href={ROUTES.course} sx={{ alignSelf: "flex-start" }}>
        Back to the course
      </Button>
      <ItemDetails item={item} playback={playback} />
      <SentenceList headingLevel="h2" sentences={item.examples} title="Sentences you have got right" />
    </Stack>
  );
}
