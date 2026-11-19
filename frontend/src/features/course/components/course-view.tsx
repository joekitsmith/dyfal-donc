import Box from "@mui/material/Box";

import { ErrorCard } from "@/components/error-card";
import { LoadingBlocks } from "@/components/loading-blocks";
import { PageHeader } from "@/components/page-header";
import { SearchField } from "@/components/search-field";
import { ReportDialog } from "@/features/problem-report";
import { textStyle } from "@/theme/text-style";

import { useCoursePage } from "../hooks/use-course-page";
import { LaterTopics } from "./later-topics";
import { SearchResults } from "./search-results";
import { TopicRow } from "./topic-row";
import { TopicSection } from "./topic-section";

type CourseViewProps = {
  /** Where the way back leads. */
  readonly back: { readonly href: string } | { readonly onClick: () => void };
  /** Opens a word or phrase in place of going to its page, for a sheet that has no pages to go to. */
  readonly onOpenItem?: (itemId: string) => void;
};

const LOADING_BLOCK_HEIGHTS = [72, 72, 72] as const;

/** Everything the learner has met, with the way to search it. The page and the sheet both show it. */
export function CourseView({ back, onOpenItem }: CourseViewProps) {
  const { error, isLoading, report, retry, search, topics } = useCoursePage();

  return (
    <>
      <PageHeader back={back} title="Everything you've met" />
      {error === null ? (
        <>
          <Box sx={{ mt: "16px" }}>
            <SearchField label="Search in English or Welsh" onChange={search.onChange} value={search.value} />
          </Box>
          {isLoading ? (
            <LoadingBlocks heights={LOADING_BLOCK_HEIGHTS} />
          ) : search.active ? (
            <SearchResults {...(onOpenItem === undefined ? {} : { onOpenItem })} results={search.results} />
          ) : (
            <>
              {topics.started.length === 0 ? (
                <Box sx={{ ...textStyle("label"), fontWeight: 400, mt: "28px" }}>
                  Words and sentences appear here as you meet them.
                </Box>
              ) : null}
              {topics.started.map(({ open, topic }) =>
                open ? (
                  <TopicSection
                    key={topic.name}
                    {...(onOpenItem === undefined ? {} : { onOpenItem })}
                    onReport={report.reportSentence}
                    topic={topic}
                  />
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
    </>
  );
}
