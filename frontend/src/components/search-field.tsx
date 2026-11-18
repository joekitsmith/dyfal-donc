import Box from "@mui/material/Box";

import { FOCUS_RING } from "@/theme/tokens";

import { SearchIcon } from "./icons/search-icon";

type SearchFieldProps = {
  readonly label: string;
  readonly onChange: (value: string) => void;
  readonly value: string;
};

const FIELD_HEIGHT = 48;

export function SearchField({ label, onChange, value }: SearchFieldProps) {
  return (
    <Box
      sx={{
        "&:focus-within": {
          outline: `${FOCUS_RING.width}px solid var(--dd-accent)`,
          outlineOffset: `${FOCUS_RING.offset}px`,
        },
        alignItems: "center",
        backgroundColor: "var(--dd-surface)",
        borderRadius: "10px",
        boxSizing: "border-box",
        color: "var(--dd-muted)",
        display: "flex",
        gap: "10px",
        height: FIELD_HEIGHT,
        px: "14px",
      }}
    >
      <SearchIcon size={20} />
      <Box
        aria-label={label}
        component="input"
        onChange={(event: { target: { value: string } }) => {
          onChange(event.target.value);
        }}
        placeholder={label}
        sx={{
          // The browser's own clear button is drawn in its own colours
          "&::-webkit-search-cancel-button": { appearance: "none" },
          "&::placeholder": { color: "var(--dd-muted)", opacity: 1 },
          "&:focus-visible": { outline: "none" },
          backgroundColor: "transparent",
          border: 0,
          color: "var(--dd-ink)",
          flex: 1,
          fontSize: "1.0625rem",
          height: 44,
          minWidth: 0,
          p: 0,
        }}
        type="search"
        value={value}
      />
    </Box>
  );
}
