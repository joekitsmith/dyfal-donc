import Box from "@mui/material/Box";

import { useDelayed } from "@/hooks/use-delayed";

type LoadingBlocksProps = {
  /** One empty block for each, at the height of what will be there. */
  readonly heights: readonly number[];
};

const SHOW_AFTER_MILLISECONDS = 300;

/** Where content will be while it loads. A load that is quick shows nothing at all, and nothing here moves. */
export function LoadingBlocks({ heights }: LoadingBlocksProps) {
  const visible = useDelayed(SHOW_AFTER_MILLISECONDS);

  if (!visible) {
    return null;
  }

  return (
    <Box aria-hidden="true" sx={{ display: "flex", flexDirection: "column", gap: "12px", mt: "24px" }}>
      {heights.map((height, index) => (
        <Box key={index} sx={{ backgroundColor: "var(--dd-surface)", borderRadius: "10px", height }} />
      ))}
    </Box>
  );
}
