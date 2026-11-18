"use client";

import Box from "@mui/material/Box";

import { ErrorCard } from "@/components/error-card";
import { LoadingBlocks } from "@/components/loading-blocks";
import { PageColumn } from "@/components/page-column";
import { PageHeader } from "@/components/page-header";
import { SentenceList } from "@/components/sentence-list";
import { SubHeading } from "@/components/sub-heading";
import { TextButton } from "@/components/text-button";
import { ROUTES } from "@/config/paths";
import { ReportDialog } from "@/features/problem-report";
import { textStyle } from "@/theme/text-style";

import { ItemDetails } from "./components/item-details";
import { useItemPage } from "./hooks/use-item-page";

type ItemPageProps = { readonly itemId: string };

const LOADING_BLOCK_HEIGHTS = [120, 120] as const;
const EXAMPLES_TITLE = "Sentences you've said with it";

export function ItemPage({ itemId }: ItemPageProps) {
  const { error, isLoading, item, notFound, playback, report, retry } = useItemPage(itemId);

  return (
    <PageColumn>
      <PageHeader back={{ href: ROUTES.course }} backLabel="Everything you've met" />
      {notFound ? (
        <Box sx={{ ...textStyle("label"), fontWeight: 400, mt: "28px" }}>We couldn&apos;t find that.</Box>
      ) : error !== null ? (
        <Box sx={{ mt: "24px" }}>
          <ErrorCard
            action={{ label: "Try again", onClick: retry }}
            text="Check your connection, then try again."
            title="We couldn't load this"
          />
        </Box>
      ) : isLoading || item === undefined ? (
        <LoadingBlocks heights={LOADING_BLOCK_HEIGHTS} />
      ) : (
        <>
          <ItemDetails item={item} playback={playback} />
          {item.examples.length === 0 ? (
            <>
              <SubHeading level="h2">{EXAMPLES_TITLE}</SubHeading>
              <Box sx={{ ...textStyle("body"), color: "var(--dd-muted)" }}>
                Sentences with this in will appear here.
              </Box>
            </>
          ) : (
            <SentenceList
              headingLevel="h2"
              onReport={report.reportSentence}
              sentences={item.examples}
              title={EXAMPLES_TITLE}
            />
          )}
          <TextButton
            onClick={() => {
              report.reportItem(item);
            }}
          >
            Report a problem with this {item.kind === "word" ? "word" : "phrase"}
          </TextButton>
        </>
      )}
      <ReportDialog {...report.dialog} />
    </PageColumn>
  );
}
