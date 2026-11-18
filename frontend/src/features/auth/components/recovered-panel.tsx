import Box from "@mui/material/Box";

import { TickIcon } from "@/components/icons/tick-icon";
import { LeadText } from "@/components/lead-text";
import { TextLink } from "@/components/text-link";
import { ROUTES } from "@/config/paths";
import { textStyle } from "@/theme/text-style";

import { AddPasskeyForm } from "./add-passkey-form";

/** What the recovery screen shows once a code has worked: a prompt to replace the lost passkey. */
export function RecoveredPanel() {
  return (
    <Box sx={{ mt: "24px" }}>
      <Box role="status" sx={{ ...textStyle("title"), alignItems: "center", display: "flex", gap: "10px" }}>
        <Box component="span" sx={{ color: "var(--dd-accent)", display: "flex" }}>
          <TickIcon size={24} />
        </Box>
        You&apos;re signed in
      </Box>
      <Box sx={{ mt: "8px" }}>
        <LeadText>Add a new passkey now, so you won&apos;t need another code next time.</LeadText>
      </Box>
      <Box sx={{ mt: "20px" }}>
        <AddPasskeyForm
          label="Name for this passkey (optional)"
          placeholder="For example, My phone"
          submit={{ label: "Add a passkey", variant: "primary" }}
        />
      </Box>
      <Box sx={{ mt: "12px" }}>
        <TextLink href={ROUTES.home}>Carry on without one</TextLink>
      </Box>
    </Box>
  );
}
