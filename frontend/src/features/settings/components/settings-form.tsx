import Alert from "@mui/material/Alert";
import Button from "@mui/material/Button";
import MenuItem from "@mui/material/MenuItem";
import Slider from "@mui/material/Slider";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { Controller } from "react-hook-form";

import type { UserSettings } from "../types";

import {
  THINK_MULTIPLIER_MAXIMUM,
  THINK_MULTIPLIER_MINIMUM,
  THINK_MULTIPLIER_STEP,
  WELSH_PLAYBACK_OPTIONS,
} from "../constants";
import { useSettingsForm } from "../hooks/use-settings-form";

type SettingsFormProps = { readonly settings: UserSettings };

export function SettingsForm({ settings }: SettingsFormProps) {
  const { control, isSaving, onSubmit, saved, saveFailed } = useSettingsForm(settings);

  return (
    <Stack
      component="form"
      noValidate
      onSubmit={(event) => {
        void onSubmit(event);
      }}
      spacing={3}
    >
      <Controller
        control={control}
        name="thinkTimeMultiplier"
        render={({ field }) => (
          <Stack>
            <Typography id="think-time-label">Think time: {field.value}×</Typography>
            <Slider
              aria-labelledby="think-time-label"
              max={THINK_MULTIPLIER_MAXIMUM}
              min={THINK_MULTIPLIER_MINIMUM}
              onChange={(_event, next) => {
                field.onChange(next);
              }}
              step={THINK_MULTIPLIER_STEP}
              value={field.value}
            />
          </Stack>
        )}
      />
      <Controller
        control={control}
        name="welshPlayback"
        render={({ field }) => (
          <TextField label="Welsh audio" select {...field}>
            {WELSH_PLAYBACK_OPTIONS.map((option) => (
              <MenuItem key={option.value} value={option.value}>
                {option.label}
              </MenuItem>
            ))}
          </TextField>
        )}
      />
      <Button disabled={isSaving} type="submit" variant="contained">
        Save
      </Button>
      {saved ? <Alert severity="success">Saved</Alert> : null}
      {saveFailed ? <Alert severity="error">The settings could not be saved. Try again.</Alert> : null}
    </Stack>
  );
}
