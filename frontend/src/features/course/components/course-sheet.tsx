"use client";

import Drawer from "@mui/material/Drawer";

import { PageColumn } from "@/components/page-column";
import { MOTION, SLOW_MILLISECONDS } from "@/theme/tokens";

import type { useCourseSheet } from "../hooks/use-course-sheet";

import { CourseView } from "./course-view";
import { ItemView } from "./item-view";

type CourseSheetProps = { readonly sheet: ReturnType<typeof useCourseSheet> };

// The lesson's shortcuts stand aside while something with this role is open
const DIALOG_ATTRIBUTES = { "aria-modal": true, role: "dialog" } as const;

/** Everything the learner has met, over the screen they were on, which keeps its place beneath. */
export function CourseSheet({ sheet }: CourseSheetProps) {
  return (
    <Drawer
      anchor="bottom"
      onClose={sheet.close}
      open={sheet.isOpen}
      slotProps={{
        backdrop: { sx: { backgroundColor: "var(--dd-scrim)" } },
        paper: {
          ...DIALOG_ATTRIBUTES,
          "aria-label": "Everything you've met",
          sx: { backgroundColor: "var(--dd-ground)", backgroundImage: "none", height: "100dvh" },
        },
        transition: { easing: MOTION.ease },
      }}
      transitionDuration={SLOW_MILLISECONDS}
    >
      <PageColumn>
        {sheet.item.id === null ? (
          <CourseView back={{ onClick: sheet.close }} onOpenItem={sheet.item.open} />
        ) : (
          <ItemView back={{ onClick: sheet.item.close }} itemId={sheet.item.id} />
        )}
      </PageColumn>
    </Drawer>
  );
}
