import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";

import type { UserSettings } from "../types";

import { useSaveSettings } from "../api/use-save-settings";
import { THINK_MULTIPLIER_MAXIMUM, THINK_MULTIPLIER_MINIMUM, WELSH_PLAYBACK_OPTIONS } from "../constants";

const schema = z.object({
  thinkTimeMultiplier: z.number().min(THINK_MULTIPLIER_MINIMUM).max(THINK_MULTIPLIER_MAXIMUM),
  welshPlayback: z.enum(WELSH_PLAYBACK_OPTIONS.map((option) => option.value)),
});

/** The settings form: it saves all the settings on submit and then shows them as the saved ones. */
export function useSettingsForm(settings: UserSettings) {
  const { control, formState, handleSubmit, reset } = useForm<UserSettings>({
    defaultValues: settings,
    resolver: zodResolver(schema),
  });
  const { isError, isPending, isSuccess, mutate } = useSaveSettings();

  return {
    control,
    onSubmit: handleSubmit((values) => {
      mutate(values, {
        onSuccess: (saved) => {
          reset(saved);
        },
      });
    }),
    save: {
      failed: isError,
      status: saveStatus({ changed: formState.isDirty, saved: isSuccess, saving: isPending }),
    },
  };
}

/** What the Save button says. Saved stays until the next change. */
function saveStatus({
  changed,
  saved,
  saving,
}: {
  readonly changed: boolean;
  readonly saved: boolean;
  readonly saving: boolean;
}): "changed" | "idle" | "saved" | "saving" {
  if (saving) {
    return "saving";
  }

  if (changed) {
    return "changed";
  }

  return saved ? "saved" : "idle";
}
