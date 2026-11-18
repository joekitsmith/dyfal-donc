import Box from "@mui/material/Box";

import { Button } from "@/components/button";
import { ChoiceRow } from "@/components/choice-row";
import { Dialog } from "@/components/dialog";
import { DialogText } from "@/components/dialog-text";
import { textStyle } from "@/theme/text-style";

import { useRecoveryCodesDialog } from "../hooks/use-recovery-codes-dialog";

/** Shows new recovery codes once. It cannot be closed until the person says they have saved them. */
export function RecoveryCodesDialog() {
  const { codes, copy, done, download, open, saved } = useRecoveryCodesDialog();

  return (
    <Dialog open={open} title="Save your recovery codes">
      <DialogText>
        If you ever lose every passkey, one of these gets you back in. Each works once. This is the only time they are
        shown.
      </DialogText>
      <Box
        aria-label="Recovery codes"
        component="ul"
        sx={{
          ...textStyle("label"),
          backgroundColor: "var(--dd-ground)",
          borderRadius: "10px",
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          letterSpacing: "0.03em",
          listStyle: "none",
          m: "16px 0 0",
          p: "14px 16px",
          rowGap: "6px",
          userSelect: "text",
        }}
      >
        {codes.map((code) => (
          <li key={code}>{code}</li>
        ))}
      </Box>
      <Box sx={{ display: "flex", gap: "12px", mt: "16px" }}>
        <Box sx={{ flex: 1 }}>
          <Button edge full onClick={copy.onClick} variant="ghost">
            {copy.copied ? "Copied" : "Copy"}
          </Button>
        </Box>
        <Box sx={{ flex: 1 }}>
          <Button edge full onClick={download} variant="ghost">
            Download
          </Button>
        </Box>
      </Box>
      <Box sx={{ mt: "4px" }}>
        <ChoiceRow checked={saved.checked} label="I have saved these codes" onChange={saved.onChange} />
      </Box>
      <Button full onClick={done.onClick} unavailable={done.disabled} variant="primary">
        Done
      </Button>
    </Dialog>
  );
}
