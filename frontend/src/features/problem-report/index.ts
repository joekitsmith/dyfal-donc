"use client";

// A client module, so the pages that import this feature on the server get components and not hooks
export { ReportDialog } from "./components/report-dialog";
export { useReportDialog } from "./hooks/use-report-dialog";
export type { ReportSubject } from "./types";
