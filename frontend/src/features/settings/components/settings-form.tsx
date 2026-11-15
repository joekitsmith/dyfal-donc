import Alert from "@mui/material/Alert";
import Button from "@mui/material/Button";
import FormControlLabel from "@mui/material/FormControlLabel";
import MenuItem from "@mui/material/MenuItem";
import Slider from "@mui/material/Slider";
import Stack from "@mui/material/Stack";
import Switch from "@mui/material/Switch";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { Controller } from "react-hook-form";

import type { UserSettings } from "../types";

import {
  LEARNING_SESSION_MINUTES,
  NO_LIMIT,
  THINK_MULTIPLIER_MAXIMUM,
  THINK_MULTIPLIER_MINIMUM,
  THINK_MULTIPLIER_STEP,
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
        name="slowWelshEnabled"
        render={({ field }) => (
          <FormControlLabel
            control={
              <Switch
                checked={field.value}
                onChange={(event) => {
                  field.onChange(event.target.checked);
                }}
              />
            }
            label="Play the slow Welsh after the Welsh"
          />
        )}
      />
      <Controller
        control={control}
        name="learningSessionMinutes"
        render={({ field }) => (
          <TextField label="Learning session length" select {...field}>
            {LEARNING_SESSION_MINUTES.map((minutes) => (
              <MenuItem key={minutes} value={String(minutes)}>
                {minutes} minutes
              </MenuItem>
            ))}
            <MenuItem value={NO_LIMIT}>No limit</MenuItem>
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
