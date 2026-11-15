import type { ApiClient } from "@/api/client";
import type { components } from "@/api/schema";

import { unwrap } from "@/api/api-error";

import type { UserSettings } from "../types";

export async function getSettings(client: ApiClient): Promise<UserSettings> {
  return toUserSettings(unwrap(await client.GET("/me/settings")));
}

/** Changes the settings named and returns all of them as they now are. */
export async function saveSettings(client: ApiClient, changes: Partial<UserSettings>): Promise<UserSettings> {
  const saved = unwrap(
    await client.PATCH("/me/settings", {
      body: {
        ...(changes.welshPlayback === undefined ? {} : { welsh_playback: changes.welshPlayback }),
        ...(changes.thinkTimeMultiplier === undefined ? {} : { think_time_multiplier: changes.thinkTimeMultiplier }),
      },
    }),
  );

  return toUserSettings(saved);
}

function toUserSettings(response: components["schemas"]["UserSettingsResponse"]): UserSettings {
  return {
    thinkTimeMultiplier: response.think_time_multiplier,
    welshPlayback: response.welsh_playback,
  };
}
