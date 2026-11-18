import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Link from "next/link";

import { ROUTES } from "@/config/paths";
import { ReportDialog, useReportDialog } from "@/features/problem-report";

/** The way to the other screens until the menu replaces it. */
export function HomeLinks() {
  const report = useReportDialog("general");

  return (
    <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1, mt: 2 }}>
      <Button component={Link} href={ROUTES.course}>
        Course
      </Button>
      <Button component={Link} href={ROUTES.settings}>
        Settings
      </Button>
      <Button component={Link} href={ROUTES.account}>
        Account
      </Button>
      <Button onClick={report.reportNothingInParticular}>Report a problem</Button>
      <ReportDialog {...report.dialog} />
    </Box>
  );
}
