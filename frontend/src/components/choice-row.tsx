import Box from "@mui/material/Box";

import { textStyle } from "@/theme/text-style";

type ChoiceRowProps = {
  readonly checked: boolean;
  readonly label: string;
  readonly onChange: (checked: boolean) => void;
};

const ROW_HEIGHT = 56;
const CHECKBOX_SIZE = 24;

/** A checkbox in a row that can be tapped anywhere along its length. */
export function ChoiceRow({ checked, label, onChange }: ChoiceRowProps) {
  return (
    <Box
      component="label"
      sx={{ ...textStyle("body"), alignItems: "center", display: "flex", gap: "12px", minHeight: ROW_HEIGHT }}
    >
      <Box
        checked={checked}
        component="input"
        onChange={(event: { target: { checked: boolean } }) => {
          onChange(event.target.checked);
        }}
        sx={{ accentColor: "var(--dd-ink)", flexShrink: 0, height: CHECKBOX_SIZE, m: 0, width: CHECKBOX_SIZE }}
        type="checkbox"
      />
      {label}
    </Box>
  );
}
