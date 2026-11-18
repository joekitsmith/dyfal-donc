import Box from "@mui/material/Box";
import ButtonBase from "@mui/material/ButtonBase";

import { textStyle } from "@/theme/text-style";

import type { Passkey } from "../types";

import { describePasskey, passkeyName } from "../utils/describe-passkey";

type PasskeyListItemProps = {
  readonly onRemove: () => void;
  readonly passkey: Passkey;
  readonly removable: boolean;
};

export function PasskeyListItem({ onRemove, passkey, removable }: PasskeyListItemProps) {
  const name = passkeyName(passkey);

  return (
    <Box
      component="li"
      sx={{
        alignItems: "center",
        display: "flex",
        gap: "12px",
        justifyContent: "space-between",
        minHeight: 64,
        py: "10px",
      }}
    >
      <Box>
        <Box sx={{ ...textStyle("label"), fontWeight: 600 }}>{name}</Box>
        <Box sx={{ color: "var(--dd-muted)", fontSize: "0.8125rem", lineHeight: 1.35, mt: "2px" }}>
          {describePasskey(passkey)}
        </Box>
      </Box>
      {removable ? (
        <ButtonBase
          aria-label={`Remove ${name}`}
          onClick={onRemove}
          sx={{ ...textStyle("body"), minHeight: 48, textDecoration: "underline" }}
        >
          Remove
        </ButtonBase>
      ) : null}
    </Box>
  );
}
