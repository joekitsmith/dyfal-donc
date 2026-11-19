import Box from "@mui/material/Box";

import { ChoiceRow } from "@/components/choice-row";
import { ListCard } from "@/components/list-card";
import { textStyle } from "@/theme/text-style";

import type { UserSettings } from "../types";

import { WELSH_PLAYBACK_OPTIONS } from "../constants";

type WelshAudioFieldProps = {
  readonly onChange: (value: UserSettings["welshPlayback"]) => void;
  readonly value: UserSettings["welshPlayback"];
};

export function WelshAudioField({ onChange, value }: WelshAudioFieldProps) {
  return (
    <Box component="fieldset" sx={{ border: 0, m: 0, minWidth: 0, p: 0 }}>
      <Box component="legend" sx={{ ...textStyle("label"), fontWeight: 600, mb: "8px", p: 0 }}>
        Welsh audio
      </Box>
      <ListCard>
        {WELSH_PLAYBACK_OPTIONS.map((option) => (
          <li key={option.value}>
            <ChoiceRow
              checked={option.value === value}
              label={option.label}
              name="welsh-audio"
              onChange={() => {
                onChange(option.value);
              }}
              type="radio"
              value={option.value}
            />
          </li>
        ))}
      </ListCard>
    </Box>
  );
}
