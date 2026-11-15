import { useQuery } from "@tanstack/react-query";

import { apiClient } from "@/api/client";

import { COURSE_QUERY_KEY } from "../constants";
import { getCourse } from "./course-requests";

/** Every topic and what the learner has met in it. It is read again on each visit, because answering changes it. */
export function useCourse() {
  return useQuery({
    queryFn: () => getCourse(apiClient),
    queryKey: COURSE_QUERY_KEY,
    refetchOnMount: "always",
  });
}
