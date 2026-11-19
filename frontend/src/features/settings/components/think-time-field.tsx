import Box from "@mui/material/Box";
import { useId } from "react";

import { textStyle } from "@/theme/text-style";

import { THINK_MULTIPLIER_MAXIMUM, THINK_MULTIPLIER_MINIMUM, THINK_MULTIPLIER_STEP } from "../constants";
import { ThinkTimePreview } from "./think-time-preview";

type ThinkTimeFieldProps = {
  readonly onChange: (value: number) => void;
  readonly value: number;
};

const HIT_HEIGHT = 48;
const END_LABEL = { color: "var(--dd-muted)", fontSize: "0.8125rem", lineHeight: 1.35 } as const;

export function ThinkTimeField({ onChange, value }: ThinkTimeFieldProps) {
  const labelId = useId();

  return (
    <section>
      <Box sx={{ alignItems: "baseline", display: "flex", justifyContent: "space-between" }}>
        <Box id={labelId} sx={{ ...textStyle("label"), fontWeight: 600 }}>
          Think time
        </Box>
        <Box sx={textStyle("label")}>{value}×</Box>
      </Box>
      <Box sx={{ ...textStyle("body"), color: "var(--dd-muted)", mt: "4px" }}>How long you get to say the Welsh.</Box>
      <Box
        aria-labelledby={labelId}
        component="input"
        max={THINK_MULTIPLIER_MAXIMUM}
        min={THINK_MULTIPLIER_MINIMUM}
        onChange={(event: { target: { valueAsNumber: number } }) => {
          onChange(event.target.valueAsNumber);
        }}
        step={THINK_MULTIPLIER_STEP}
        sx={{ accentColor: "var(--dd-ink)", display: "block", height: HIT_HEIGHT, m: "4px 0 0", width: "100%" }}
        type="range"
        value={value}
      />
      <Box sx={{ ...END_LABEL, display: "flex", justifyContent: "space-between" }}>
        <span>{THINK_MULTIPLIER_MINIMUM}×</span>
        <span>{THINK_MULTIPLIER_MAXIMUM}×</span>
      </Box>
      <ThinkTimePreview multiplier={value} />
    </section>
  );
}
