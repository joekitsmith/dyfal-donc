import Box from "@mui/material/Box";

const BLOCK_COLOURS = ["var(--dd-ink)", "var(--dd-ink)", "var(--dd-accent)"] as const;

export function AppMark() {
  return (
    <Box aria-hidden="true" component="span" sx={{ display: "flex", gap: "3px" }}>
      {BLOCK_COLOURS.map((colour, index) => (
        <Box component="span" key={index} sx={{ backgroundColor: colour, borderRadius: "2px", height: 20, width: 7 }} />
      ))}
    </Box>
  );
}
