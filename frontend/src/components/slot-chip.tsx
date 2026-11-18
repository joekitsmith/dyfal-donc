import Box from "@mui/material/Box";

type SlotChipProps = { readonly name: string };

/** The place in a pattern where a word goes, drawn like a beat still to come. */
export function SlotChip({ name }: SlotChipProps) {
  return (
    <Box
      component="span"
      lang="en"
      sx={{
        border: "2px dashed var(--dd-line)",
        borderRadius: "5px",
        color: "var(--dd-muted)",
        fontSize: "0.8125rem",
        fontWeight: 400,
        lineHeight: "20px",
        px: "7px",
      }}
    >
      {name}
    </Box>
  );
}
