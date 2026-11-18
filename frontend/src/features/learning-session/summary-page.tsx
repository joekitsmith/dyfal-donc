"use client";

import Box from "@mui/material/Box";

import { Button } from "@/components/button";
import { ErrorCard } from "@/components/error-card";
import { LeadText } from "@/components/lead-text";
import { LoadingBlocks } from "@/components/loading-blocks";
import { PageColumn } from "@/components/page-column";
import { PageHeader } from "@/components/page-header";
import { SentenceList } from "@/components/sentence-list";
import { ROUTES } from "@/config/paths";
import { ReportDialog } from "@/features/problem-report";
import { textStyle } from "@/theme/text-style";

import { ItemSection } from "./components/item-section";
import { useSummaryPage } from "./hooks/use-summary-page";
import { formatDuration } from "./utils/format-time";

type SummaryPageProps = { readonly sessionId: number };

const LOADING_BLOCK_HEIGHTS = [48, 156] as const;

export function SummaryPage({ sessionId }: SummaryPageProps) {
  const { error, isLoading, notFound, report, retry, summary } = useSummaryPage(sessionId);
  const title = summary?.ongoing === true ? "This session so far" : "Last time";

  return (
    <PageColumn>
      <PageHeader back={{ href: ROUTES.home }} title={title} />
      {notFound ? (
        <Box sx={{ mt: "24px" }}>
          <LeadText>We couldn&apos;t find that session.</LeadText>
        </Box>
      ) : error === null ? (
        summary === undefined || isLoading ? (
          <LoadingBlocks heights={LOADING_BLOCK_HEIGHTS} />
        ) : (
          <>
            <Box sx={{ ...textStyle("sentence-en"), m: "24px 0 0" }}>
              {summary.exercises_completed === 1 ? "1 sentence" : `${summary.exercises_completed} sentences`} in{" "}
              {formatDuration(summary.duration_seconds)}
              {summary.ongoing ? ", and still going." : "."}
            </Box>
            {summary.items_reviewed > 0 ? (
              <Box sx={{ ...textStyle("body"), color: "var(--dd-muted)", mt: "8px" }}>
                {summary.items_reviewed === 1 ? "1 word" : `${summary.items_reviewed} words`} you already knew came
                round again.
              </Box>
            ) : null}
            <ItemSection items={summary.items_introduced} title="New" />
            <ItemSection
              items={summary.items_lapsed}
              note="Older words from sentences you marked."
              title="Coming back sooner"
            />
            <SentenceList
              headingLevel="h2"
              onReport={report.reportSentence}
              sentences={summary.missed_exercises}
              title="Sentences you marked"
            />
            <Box sx={{ mt: "28px" }}>
              <Button href={ROUTES.home} variant="primary">
                Back to the lesson
              </Button>
            </Box>
          </>
        )
      ) : (
        <Box sx={{ mt: "24px" }}>
          <ErrorCard
            action={{ label: "Try again", onClick: retry }}
            text="Check your connection, then try again."
            title="We couldn't load this"
          />
        </Box>
      )}
      <ReportDialog {...report.dialog} />
    </PageColumn>
  );
}
