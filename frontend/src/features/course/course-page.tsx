"use client";

import { PageColumn } from "@/components/page-column";
import { ROUTES } from "@/config/paths";

import { CourseView } from "./components/course-view";

export function CoursePage() {
  return (
    <PageColumn>
      <CourseView back={{ href: ROUTES.home }} />
    </PageColumn>
  );
}
