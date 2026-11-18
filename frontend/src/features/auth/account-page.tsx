"use client";

import Box from "@mui/material/Box";

import { ErrorCard } from "@/components/error-card";
import { LeadText } from "@/components/lead-text";
import { LoadingBlocks } from "@/components/loading-blocks";
import { NoticeCard } from "@/components/notice-card";
import { PageColumn } from "@/components/page-column";
import { PageHeader } from "@/components/page-header";
import { SubHeading } from "@/components/sub-heading";
import { ROUTES } from "@/config/paths";
import { textStyle } from "@/theme/text-style";

import { AddPasskeyForm } from "./components/add-passkey-form";
import { DeleteAccountButton } from "./components/delete-account-button";
import { PasskeyList } from "./components/passkey-list";
import { RecoveryCodesSection } from "./components/recovery-codes-section";
import { SaveProgressPrompt } from "./components/save-progress-prompt";
import { SignOutButton } from "./components/sign-out-button";
import { useAccount } from "./hooks/use-account";

const LOADING_BLOCK_HEIGHTS = [72, 72] as const;

export function AccountPage() {
  const { deleteAccount, error, failure, isLoading, passkeys, recovery, retry, signOut, user } = useAccount();

  return (
    <PageColumn>
      <PageHeader back={{ href: ROUTES.home }} title="Account" />
      {error !== null ? (
        <Box sx={{ mt: "24px" }}>
          <ErrorCard
            action={{ label: "Try again", onClick: retry }}
            text="Check your connection, then try again."
            title="We couldn't load this"
          />
        </Box>
      ) : isLoading || user === undefined ? (
        <LoadingBlocks heights={LOADING_BLOCK_HEIGHTS} />
      ) : (
        <>
          {failure === null ? null : (
            <Box sx={{ mt: "16px" }}>
              <NoticeCard role="status">{failure}</NoticeCard>
            </Box>
          )}
          <Box sx={{ mt: "24px" }}>
            <LeadText>{user.isGuest ? "You're using a guest account." : "You're signed in with a passkey."}</LeadText>
          </Box>
          {user.isGuest ? (
            <Box sx={{ mt: "16px" }}>
              <SaveProgressPrompt />
            </Box>
          ) : null}
          <section aria-label="Passkeys">
            <SubHeading level="h2">Passkeys</SubHeading>
            {passkeys.items.length === 0 ? (
              <Box sx={{ ...textStyle("body"), color: "var(--dd-muted)" }}>None yet.</Box>
            ) : (
              <PasskeyList onRemove={passkeys.remove} passkeys={passkeys.items} />
            )}
          </section>
          {user.isGuest ? null : (
            <>
              <Box sx={{ mt: "16px" }}>
                <AddPasskeyForm
                  buttonGap="12px"
                  label="Name for a new passkey (optional)"
                  submit={{ label: "Add another passkey", variant: "quiet" }}
                />
              </Box>
              <RecoveryCodesSection codes={recovery} />
            </>
          )}
          <Box sx={{ borderTop: "2px solid var(--dd-line)", mt: "32px", pt: "20px" }}>
            <SignOutButton isGuest={user.isGuest} onSignOut={signOut} />
            <Box sx={{ mt: "4px" }}>
              <DeleteAccountButton onDelete={deleteAccount} />
            </Box>
          </Box>
        </>
      )}
    </PageColumn>
  );
}
