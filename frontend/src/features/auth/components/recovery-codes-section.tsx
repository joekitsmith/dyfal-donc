import Box from "@mui/material/Box";

import { Button } from "@/components/button";
import { SubHeading } from "@/components/sub-heading";
import { useDisclosure } from "@/hooks/use-disclosure";
import { textStyle } from "@/theme/text-style";

import type { useRecoveryCodesSection } from "../hooks/use-recovery-codes-section";

import { RECOVERY_CODE_TOTAL } from "../constants";
import { ConfirmDialog } from "./confirm-dialog";

type RecoveryCodesSectionProps = { readonly codes: ReturnType<typeof useRecoveryCodesSection> };

export function RecoveryCodesSection({ codes }: RecoveryCodesSectionProps) {
  const { generate, isGenerating, isLoading, low, remaining } = codes;
  const dialog = useDisclosure();

  if (isLoading || remaining === undefined) {
    return null;
  }

  return (
    <section aria-label="Recovery codes">
      <SubHeading level="h2">Recovery codes</SubHeading>
      <Box sx={textStyle("body")}>
        {remaining} of {RECOVERY_CODE_TOTAL} left. Each one gets you back in once if you lose every passkey.
      </Box>
      {low ? (
        <Box
          role="status"
          sx={{
            ...textStyle("body"),
            border: "2px solid var(--dd-ink)",
            borderRadius: "10px",
            fontWeight: 500,
            mt: "12px",
            p: "12px 14px",
          }}
        >
          {remaining === 0
            ? "No codes left. Make new ones now."
            : `Only ${remaining} ${remaining === 1 ? "code" : "codes"} left. Make new ones soon.`}
        </Box>
      ) : null}
      <Box sx={{ mt: "12px" }}>
        <Button onClick={dialog.open} unavailable={isGenerating} variant="quiet">
          Make new codes
        </Button>
      </Box>
      <ConfirmDialog
        buttons={[
          {
            emphasis: "primary",
            label: "Make new codes",
            onClick: () => {
              dialog.close();
              generate();
            },
          },
          { emphasis: "ghost", label: "Cancel", onClick: dialog.close },
        ]}
        description="Your current codes will stop working."
        onClose={dialog.close}
        open={dialog.isOpen}
        title="Make new recovery codes?"
      />
    </section>
  );
}
