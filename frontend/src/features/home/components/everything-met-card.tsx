import Box from "@mui/material/Box";

import { NoticeCard } from "@/components/notice-card";
import { TextLink } from "@/components/text-link";
import { ROUTES } from "@/config/paths";
import { textStyle } from "@/theme/text-style";

export function EverythingMetCard() {
  return (
    <NoticeCard
      actions={
        <TextLink href={ROUTES.course} inline medium>
          {"Everything you've met"}
        </TextLink>
      }
    >
      <Box sx={{ ...textStyle("label"), fontWeight: 600 }}>{"You've met everything in the course"}</Box>
      <Box sx={{ mt: "4px" }}>{"From here it's all keeping it fresh."}</Box>
    </NoticeCard>
  );
}
