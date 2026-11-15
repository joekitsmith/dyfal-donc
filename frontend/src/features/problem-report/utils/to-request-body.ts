import type { components } from "@/api/schema";

import type { ReportSource, ReportSubject, ReportValues } from "../types";

type Body = components["schemas"]["ProblemReportRequest"];

/** What the API is sent for the form once it is valid. ``subject`` is the one chosen, if any. */
export function toRequestBody(source: ReportSource, subject: ReportSubject | undefined, values: ReportValues): Body {
  return {
    category: values.category,
    description: values.description,
    exercise_id: subject?.kind === "sentence" ? subject.id : null,
    item_id: subject?.kind === "item" ? subject.id : null,
    source,
  };
}
