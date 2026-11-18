import Box from "@mui/material/Box";

import { textStyle } from "@/theme/text-style";

export function HeadphoneHint() {
  return (
    <Box sx={{ ...textStyle("hint"), color: "var(--dd-muted)", textAlign: "center" }}>
      On headphones: back replays, forward marks Missed it.
    </Box>
  );
}
