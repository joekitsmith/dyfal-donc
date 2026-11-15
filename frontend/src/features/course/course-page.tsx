"use client";

import Alert from "@mui/material/Alert";
import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import Link from "next/link";

import { ROUTES } from "@/config/paths";

import { CourseSearchBox } from "./components/course-search-box";
import { LaterTopics } from "./components/later-topics";
import { SearchResults } from "./components/search-results";
import { TopicAccordion } from "./components/topic-accordion";
import { useCoursePage } from "./hooks/use-course-page";

export function CoursePage() {
  const { error, isLoading, search, topics } = useCoursePage();

  if (error) {
    return <Alert severity="error">{error.message}</Alert>;
  }

  if (isLoading) {
    return <Typography>Loading</Typography>;
  }

  return (
    <Stack component="main" spacing={3} sx={{ maxWidth: 560, mt: { sm: 8, xs: 3 }, mx: "auto", p: 2 }}>
      <Button component={Link} href={ROUTES.home} sx={{ alignSelf: "flex-start" }}>
        Back to home
      </Button>
      <Typography component="h1" variant="h4">
        Course
      </Typography>
      <CourseSearchBox onChange={search.onChange} value={search.value} />
      {search.active ? (
        <SearchResults results={search.results} />
      ) : (
        <>
          {topics.started.length === 0 ? (
            <Typography>Words and sentences appear here as you meet them.</Typography>
          ) : null}
          <Stack>
            {topics.started.map((topic) => (
              <TopicAccordion key={topic.name} topic={topic} />
            ))}
          </Stack>
          <LaterTopics topics={topics.later} />
        </>
      )}
    </Stack>
  );
}
