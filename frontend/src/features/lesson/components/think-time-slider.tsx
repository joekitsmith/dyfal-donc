import Slider from "@mui/material/Slider";
import Typography from "@mui/material/Typography";

import { THINK_MULTIPLIER_MAXIMUM, THINK_MULTIPLIER_MINIMUM, THINK_MULTIPLIER_STEP } from "../constants";

export function ThinkTimeSlider({
  onChange,
  value,
}: {
  readonly onChange: (value: number) => void;
  readonly value: number;
}) {
  return (
    <>
      <Typography id="think-time-label">Think time: {value}×</Typography>
      <Slider
        aria-labelledby="think-time-label"
        max={THINK_MULTIPLIER_MAXIMUM}
        min={THINK_MULTIPLIER_MINIMUM}
        onChange={(_event, next) => {
          onChange(next);
        }}
        step={THINK_MULTIPLIER_STEP}
        value={value}
      />
    </>
  );
}
