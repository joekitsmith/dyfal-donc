"use client";

import Box from "@mui/material/Box";

import { LeadText } from "@/components/lead-text";
import { PageColumn } from "@/components/page-column";
import { PageHeader } from "@/components/page-header";
import { ROUTES } from "@/config/paths";

import { RecoveredPanel } from "./components/recovered-panel";
import { RecoveryCodeForm } from "./components/recovery-code-form";
import { useRecover } from "./hooks/use-recover";

export function RecoverPage() {
  const { field, isLoading, isSigningIn, onSubmit, recovered } = useRecover();

  return (
    <PageColumn>
      <PageHeader back={{ href: ROUTES.welcome }} title="Use a recovery code" />
      {isLoading ? null : recovered ? (
        <RecoveredPanel />
      ) : (
        <>
          <Box sx={{ mt: "24px" }}>
            <LeadText>Enter one of the codes you saved when you added your passkey. Each code works once.</LeadText>
          </Box>
          <RecoveryCodeForm field={field} isSigningIn={isSigningIn} onSubmit={onSubmit} />
        </>
      )}
    </PageColumn>
  );
}
