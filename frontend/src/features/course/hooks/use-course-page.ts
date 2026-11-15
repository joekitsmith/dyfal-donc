import { useMemo, useState } from "react";

import { useRequireSession } from "@/features/auth";
import { useReportDialog } from "@/features/problem-report";

import { useCourse } from "../api/use-course";
import { searchItems } from "../utils/search";

/** What the course screen shows: the topics met and still to come, and the matches for the search box. */
export function useCoursePage() {
  const { error: sessionError, user } = useRequireSession();
  const course = useCourse();
  const report = useReportDialog("course");
  const [query, setQuery] = useState("");
  const topics = useMemo(() => course.data?.topics ?? [], [course.data]);
  const results = useMemo(() => searchItems(topics, query), [topics, query]);

  return {
    error: sessionError ?? course.error,
    isLoading: user === undefined || course.isPending,
    report,
    search: {
      active: query.trim() !== "",
      onChange: setQuery,
      results,
      value: query,
    },
    topics: {
      later: topics.filter((topic) => !topic.started),
      started: topics.filter((topic) => topic.started),
    },
  };
}
