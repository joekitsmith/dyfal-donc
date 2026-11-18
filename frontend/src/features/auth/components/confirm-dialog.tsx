import type { ReactNode } from "react";

import Box from "@mui/material/Box";

import { Button } from "@/components/button";
import { Dialog } from "@/components/dialog";
import { DialogText } from "@/components/dialog-text";
import { textStyle } from "@/theme/text-style";

type ConfirmDialogProps = {
  /** Stacked, the one that goes ahead first. */
  readonly buttons: readonly DialogButton[];
  readonly description: string;
  /** Something to say above the buttons, such as why the last try did not work. */
  readonly notice?: ReactNode;
  readonly onClose: () => void;
  readonly open: boolean;
  readonly title: string;
};

type DialogButton = {
  readonly emphasis: "edge" | "ghost" | "primary";
  /** A line under the button, for what it will do. */
  readonly hint?: string;
  readonly label: string;
  readonly onClick: () => void;
  readonly unavailable?: boolean;
};

export function ConfirmDialog({ buttons, description, notice, onClose, open, title }: ConfirmDialogProps) {
  return (
    <Dialog onClose={onClose} open={open} title={title}>
      <DialogText>{description}</DialogText>
      {notice === undefined ? null : <Box sx={{ mt: "16px" }}>{notice}</Box>}
      <Box sx={{ display: "flex", flexDirection: "column", gap: "12px", mt: "16px" }}>
        {buttons.map(({ emphasis, hint, label, onClick, unavailable }) => (
          <Box key={label}>
            <Button
              edge={emphasis === "edge"}
              full
              onClick={onClick}
              unavailable={unavailable ?? false}
              variant={emphasis === "primary" ? "primary" : "ghost"}
            >
              {label}
            </Button>
            {hint === undefined ? null : (
              <Box sx={{ ...textStyle("hint"), color: "var(--dd-muted)", mt: "8px", textAlign: "center" }}>{hint}</Box>
            )}
          </Box>
        ))}
      </Box>
    </Dialog>
  );
}
