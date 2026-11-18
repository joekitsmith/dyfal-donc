import Box from "@mui/material/Box";

import { NoticeCard } from "@/components/notice-card";
import { textStyle } from "@/theme/text-style";

export function HowItGoesCard() {
  return (
    <NoticeCard>
      <Box sx={{ ...textStyle("label"), fontWeight: 600 }}>How it goes</Box>
      <Box sx={{ lineHeight: 1.45, mt: "6px" }}>
        {"You'll hear a sentence in English. Say it in Welsh, out loud. Then you'll hear it in Welsh, twice."}
      </Box>
    </NoticeCard>
  );
}
