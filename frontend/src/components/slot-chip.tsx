import Box from "@mui/material/Box";

type SlotChipProps = {
  readonly name: string;
  /** For a chip in a heading, where it has to match the text around it. */
  readonly size?: "heading" | "text";
};

const SIZES = {
  heading: { fontSize: "1.0625rem", lineHeight: "30px", px: "10px" },
  text: { fontSize: "0.8125rem", lineHeight: "20px", px: "7px" },
} as const;

/** The place in a pattern where a word goes, drawn like a beat still to come. */
export function SlotChip({ name, size = "text" }: SlotChipProps) {
  return (
    <Box
      component="span"
      lang="en"
      sx={{
        border: "2px dashed var(--dd-line)",
        borderRadius: "5px",
        color: "var(--dd-muted)",
        fontWeight: 400,
        ...SIZES[size],
      }}
    >
      {name}
    </Box>
  );
}
