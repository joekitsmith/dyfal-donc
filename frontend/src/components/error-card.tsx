import Box from "@mui/material/Box";

import { textStyle } from "@/theme/text-style";

import { Button } from "./button";

type ErrorCardProps = {
  /** Without one the card only says what happened. */
  readonly action?:
    | undefined
    | { readonly href: string; readonly label: string }
    | { readonly label: string; readonly onClick: () => void };
  readonly text: string;
  readonly title: string;
};

export function ErrorCard({ action, text, title }: ErrorCardProps) {
  return (
    <Box role="alert" sx={{ backgroundColor: "var(--dd-surface)", borderRadius: "10px", p: "16px" }}>
      <Box sx={{ ...textStyle("label"), fontWeight: 600 }}>{title}</Box>
      <Box sx={{ ...textStyle("body"), color: "var(--dd-muted)", mt: "4px" }}>{text}</Box>
      {action === undefined ? null : (
        <Box sx={{ display: "flex", mt: "12px" }}>
          {"href" in action ? (
            <Button compact href={action.href} variant="primary">
              {action.label}
            </Button>
          ) : (
            <Button compact onClick={action.onClick} variant="primary">
              {action.label}
            </Button>
          )}
        </Box>
      )}
    </Box>
  );
}
