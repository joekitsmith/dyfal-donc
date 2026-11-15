import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { useSaveSettings } from "../api/use-save-settings";
import { LEARNING_SESSION_MINUTES, NO_LIMIT, THINK_MULTIPLIER_MAXIMUM, THINK_MULTIPLIER_MINIMUM } from "../constants";
import { type LearningSessionMinutes, type UserSettings } from "../types";

const MINUTES_CHOICES = [...LEARNING_SESSION_MINUTES.map(String), NO_LIMIT] as const;

const schema = z.object({
  learningSessionMinutes: z.enum(MINUTES_CHOICES),
  slowWelshEnabled: z.boolean(),
  thinkTimeMultiplier: z.number().min(THINK_MULTIPLIER_MINIMUM).max(THINK_MULTIPLIER_MAXIMUM),
});

export type SettingsFormValues = z.infer<typeof schema>;

/** The settings form: it saves all the settings on submit and then shows them as the saved ones. */
export function useSettingsForm(settings: UserSettings) {
  const { control, formState, handleSubmit, reset } = useForm<SettingsFormValues>({
    defaultValues: toFormValues(settings),
    resolver: zodResolver(schema),
  });
  const { isError, isPending, isSuccess, mutate } = useSaveSettings();

  return {
    control,
    isSaving: isPending,
    onSubmit: handleSubmit((values) => {
      mutate(toSettings(values), {
        onSuccess: (saved) => {
          reset(toFormValues(saved));
        },
      });
    }),
    saved: isSuccess && !formState.isDirty,
    saveFailed: isError,
  };
}

function toFormValues(settings: UserSettings): SettingsFormValues {
  return {
    learningSessionMinutes:
      settings.learningSessionMinutes === null ? NO_LIMIT : String(settings.learningSessionMinutes),
    slowWelshEnabled: settings.slowWelshEnabled,
    thinkTimeMultiplier: settings.thinkTimeMultiplier,
  };
}

function toSettings(values: SettingsFormValues): UserSettings {
  return {
    learningSessionMinutes:
      values.learningSessionMinutes === NO_LIMIT
        ? null
        : (Number(values.learningSessionMinutes) as LearningSessionMinutes),
    slowWelshEnabled: values.slowWelshEnabled,
    thinkTimeMultiplier: values.thinkTimeMultiplier,
  };
}
