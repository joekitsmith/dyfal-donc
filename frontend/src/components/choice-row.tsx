import type { ReactNode } from "react";

import Box from "@mui/material/Box";

import { textStyle } from "@/theme/text-style";

type ChoiceRowProps = {
  readonly checked: boolean;
  readonly label: ReactNode;
  readonly onChange: (checked: boolean) => void;
} & (
  | { readonly name: string; readonly type: "radio"; readonly value: string }
  | { readonly name?: never; readonly type?: "checkbox"; readonly value?: never }
);

const ROW_HEIGHT = 56;
const CONTROL_SIZES = { checkbox: 24, radio: 22 } as const;

/** A checkbox or a radio button in a row that can be tapped anywhere along its length. */
export function ChoiceRow({ checked, label, name, onChange, type = "checkbox", value }: ChoiceRowProps) {
  const size = CONTROL_SIZES[type];

  return (
    <Box
      component="label"
      sx={{ ...textStyle("body"), alignItems: "center", display: "flex", gap: "12px", minHeight: ROW_HEIGHT }}
    >
      <Box
        checked={checked}
        component="input"
        name={name}
        onChange={(event: { target: { checked: boolean } }) => {
          onChange(event.target.checked);
        }}
        sx={{ accentColor: "var(--dd-ink)", flexShrink: 0, height: size, m: 0, width: size }}
        type={type}
        value={value}
      />
      {label}
    </Box>
  );
}
