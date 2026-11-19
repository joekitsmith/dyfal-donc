"use client";

import Box from "@mui/material/Box";

import { ErrorCard } from "@/components/error-card";
import { LoadingBlocks } from "@/components/loading-blocks";
import { PageColumn } from "@/components/page-column";
import { PageHeader } from "@/components/page-header";
import { ROUTES } from "@/config/paths";
import { useRequireSession } from "@/features/auth";

import { useSettings } from "./api/use-settings";
import { SettingsForm } from "./components/settings-form";

const LOADING_BLOCK_HEIGHTS = [72, 72, 72] as const;

export function SettingsPage() {
  const { error: sessionError, user } = useRequireSession();
  const settings = useSettings();
  const error = sessionError ?? settings.error;

  return (
    <PageColumn fill>
      <PageHeader back={{ href: ROUTES.home }} title="Settings" />
      {error !== null ? (
        <Box sx={{ mt: "24px" }}>
          <ErrorCard
            action={{
              label: "Try again",
              onClick: () => {
                void settings.refetch();
              },
            }}
            text="Check your connection, then try again."
            title="We couldn't load this"
          />
        </Box>
      ) : user === undefined || settings.data === undefined ? (
        <LoadingBlocks heights={LOADING_BLOCK_HEIGHTS} />
      ) : (
        <SettingsForm settings={settings.data} />
      )}
    </PageColumn>
  );
}
