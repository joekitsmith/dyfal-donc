import Box from "@mui/material/Box";
import { keyframes } from "@mui/material/styles";
import { useState } from "react";

const grow = keyframes`
  from { transform: scaleX(0); }
  to { transform: scaleX(1); }
`;

/** Fills over the think time. It is mounted when thinking starts, so it always starts empty. */
export function ThinkProgressFill({ paused, seconds }: { readonly paused: boolean; readonly seconds: number }) {
  // The duration is fixed when thinking starts, because the timer's is
  const [duration] = useState(seconds);

  return (
    <Box
      sx={{
        animation: `${grow} ${duration}s linear forwards`,
        animationPlayState: paused ? "paused" : "running",
        bgcolor: "primary.main",
        height: "100%",
        transformOrigin: "left",
      }}
    />
  );
}
