"use client";

import Box from "@mui/material/Box";

import { AppHeader } from "@/components/app-header";
import { BeatRow } from "@/components/beat-row";
import { Button } from "@/components/button";
import { LeadText } from "@/components/lead-text";
import { NoticeCard } from "@/components/notice-card";
import { Proverb } from "@/components/proverb";
import { ScreenFrame } from "@/components/screen-frame";
import { StartSlab } from "@/components/start-slab";
import { TextLink } from "@/components/text-link";
import { ROUTES } from "@/config/paths";

import { useWelcome } from "./hooks/use-welcome";

const BEAT_COUNT = 8;

export function WelcomePage() {
  const { isLoading, notice, signIn, tryIt } = useWelcome();

  return (
    <ScreenFrame
      beats={<BeatRow count={BEAT_COUNT} nowIndex={0} />}
      body={
        <>
          <Proverb language="cy" />
          <Box sx={{ mt: "12px" }}>
            <LeadText>
              Learn to speak Welsh one sentence at a time. Each word comes back just before it would fade.
            </LeadText>
          </Box>
          {notice === null ? null : (
            <Box sx={{ mt: "auto", py: "12px" }}>
              <NoticeCard role="status">{notice}</NoticeCard>
            </Box>
          )}
        </>
      }
      controls={
        isLoading ? null : (
          <>
            {signIn.supported ? (
              <Button onClick={signIn.onClick} unavailable={signIn.disabled} variant="quiet">
                Sign in with a passkey
              </Button>
            ) : null}
            <TextLink href={ROUTES.recover} unavailable={tryIt.disabled}>
              Use a recovery code
            </TextLink>
            <StartSlab
              onClick={tryIt.onClick}
              subtitle={tryIt.disabled ? "One moment…" : "No sign-up needed"}
              title="Try it now"
              unavailable={tryIt.disabled}
            />
          </>
        )
      }
      english={<Proverb language="en" />}
      header={<AppHeader />}
    />
  );
}
