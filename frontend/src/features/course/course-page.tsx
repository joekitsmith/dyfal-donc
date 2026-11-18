"use client";

import Box from "@mui/material/Box";

import { ErrorCard } from "@/components/error-card";
import { LoadingBlocks } from "@/components/loading-blocks";
import { PageColumn } from "@/components/page-column";
import { PageHeader } from "@/components/page-header";
import { SearchField } from "@/components/search-field";
import { ROUTES } from "@/config/paths";
import { ReportDialog } from "@/features/problem-report";
import { textStyle } from "@/theme/text-style";

import { LaterTopics } from "./components/later-topics";
import { SearchResults } from "./components/search-results";
import { TopicRow } from "./components/topic-row";
import { TopicSection } from "./components/topic-section";
import { useCoursePage } from "./hooks/use-course-page";

const LOADING_BLOCK_HEIGHTS = [72, 72, 72] as const;

export function CoursePage() {
  const { error, isLoading, report, retry, search, topics } = useCoursePage();

  return (
    <PageColumn>
      <PageHeader back={{ href: ROUTES.home }} title="Everything you've met" />
      {error === null ? (
        <>
          <Box sx={{ mt: "16px" }}>
            <SearchField label="Search in English or Welsh" onChange={search.onChange} value={search.value} />
          </Box>
          {isLoading ? (
            <LoadingBlocks heights={LOADING_BLOCK_HEIGHTS} />
          ) : search.active ? (
            <SearchResults results={search.results} />
          ) : (
            <>
              {topics.started.length === 0 ? (
                <Box sx={{ ...textStyle("label"), fontWeight: 400, mt: "28px" }}>
                  Words and sentences appear here as you meet them.
                </Box>
              ) : null}
              {topics.started.map(({ open, topic }) =>
                open ? (
                  <TopicSection key={topic.name} onReport={report.reportSentence} topic={topic} />
                ) : (
                  <Box key={topic.name} sx={{ mt: "12px" }}>
                    <TopicRow
                      onOpen={() => {
                        topics.onUnfold(topic.name);
                      }}
                      topic={topic}
                    />
                  </Box>
                ),
              )}
              <LaterTopics topics={topics.later} />
            </>
          )}
        </>
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
