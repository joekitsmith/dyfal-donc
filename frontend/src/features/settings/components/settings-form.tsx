import Box from "@mui/material/Box";
import { Controller } from "react-hook-form";

import { Button } from "@/components/button";
import { TickIcon } from "@/components/icons/tick-icon";
import { NoticeCard } from "@/components/notice-card";
import { textStyle } from "@/theme/text-style";

import type { UserSettings } from "../types";

import { useSettingsForm } from "../hooks/use-settings-form";
import { ThinkTimeField } from "./think-time-field";
import { WelshAudioField } from "./welsh-audio-field";

type SettingsFormProps = { readonly settings: UserSettings };

export function SettingsForm({ settings }: SettingsFormProps) {
  const { control, onSubmit, save } = useSettingsForm(settings);

  return (
    <Box
      component="form"
      noValidate
      onSubmit={(event) => {
        void onSubmit(event);
      }}
      sx={{ display: "flex", flex: 1, flexDirection: "column" }}
    >
      <Box sx={{ mt: "24px" }}>
        <Controller
          control={control}
          name="thinkTimeMultiplier"
          render={({ field }) => <ThinkTimeField onChange={field.onChange} value={field.value} />}
        />
      </Box>
      <Box sx={{ mt: "32px" }}>
        <Controller
          control={control}
          name="welshPlayback"
          render={({ field }) => <WelshAudioField onChange={field.onChange} value={field.value} />}
        />
      </Box>
      <Box sx={{ mt: "auto", pt: "32px" }}>
        {save.failed ? (
          <Box sx={{ mb: "12px" }}>
            <NoticeCard role="status">
              Your changes couldn&apos;t be saved. They&apos;re still here, so try again.
            </NoticeCard>
          </Box>
        ) : null}
        <Box sx={{ ...textStyle("hint"), color: "var(--dd-muted)", textAlign: "center" }}>
          Changes apply from the next sentence.
        </Box>
        <Box sx={{ mt: "12px" }}>
          <Button type="submit" unavailable={save.status !== "changed"} variant="primary">
            {save.status === "saving" ? "Saving…" : null}
            {save.status === "saved" ? (
              <>
                <TickIcon size={20} />
                Saved
              </>
            ) : null}
            {save.status === "idle" || save.status === "changed" ? "Save" : null}
          </Button>
        </Box>
      </Box>
    </Box>
  );
}
