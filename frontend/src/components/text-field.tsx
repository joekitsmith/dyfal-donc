import type { ComponentPropsWithRef } from "react";

import Box from "@mui/material/Box";
import { useId } from "react";

import { textStyle } from "@/theme/text-style";

type TextFieldProps = {
  /** The field takes a code, so its text is larger and spaced out. */
  readonly code?: boolean;
  /** Shown at the right of the label, as a count of what has been written. */
  readonly counter?: string;
  readonly hint?: string;
  /** Attributes for the input itself, which is where a form library puts what it registers. */
  readonly input: ComponentPropsWithRef<"input">;
  readonly label: string;
  /** Why the field is not right. It is announced when it appears. */
  readonly message?: string | undefined;
  /** A text area of this many rows, in place of a single line. */
  readonly multiline?: number;
  readonly placeholder?: string | undefined;
};

const FIELD_TEXT = { fontSize: "0.9375rem", fontWeight: 500 } as const;
const INPUT_HEIGHT = 56;

export function TextField({
  code = false,
  counter,
  hint,
  input,
  label,
  message,
  multiline,
  placeholder,
}: TextFieldProps) {
  const inputId = useId();
  const messageId = useId();
  const hintId = useId();
  const describedBy = [message === undefined ? null : messageId, hint === undefined ? null : hintId]
    .filter((identifier) => identifier !== null)
    .join(" ");

  return (
    <Box>
      <Box sx={{ alignItems: "baseline", display: "flex", justifyContent: "space-between", mb: "6px" }}>
        <Box component="label" htmlFor={inputId} sx={FIELD_TEXT}>
          {label}
        </Box>
        {counter === undefined ? null : (
          <Box sx={{ color: "var(--dd-muted)", fontSize: "0.8125rem", lineHeight: 1.35 }}>{counter}</Box>
        )}
      </Box>
      <Box
        aria-describedby={describedBy === "" ? undefined : describedBy}
        aria-invalid={message === undefined ? undefined : true}
        component={multiline === undefined ? "input" : "textarea"}
        id={inputId}
        placeholder={placeholder}
        rows={multiline}
        {...input}
        sx={{
          ...(code ? { fontSize: "1.1875rem", letterSpacing: "0.04em" } : { fontSize: "1.0625rem" }),
          "&::placeholder": { color: "var(--dd-muted)", opacity: 1 },
          backgroundColor: "var(--dd-surface)",
          border: `2px solid ${message === undefined ? "var(--dd-line)" : "var(--dd-ink)"}`,
          borderRadius: "10px",
          boxSizing: "border-box",
          color: "var(--dd-ink)",
          display: "block",
          ...(multiline === undefined
            ? { height: INPUT_HEIGHT, px: "14px" }
            : { lineHeight: 1.4, p: "12px 14px", resize: "none" }),
          width: "100%",
        }}
      />
      {message === undefined ? null : (
        <Box id={messageId} role="alert" sx={{ ...FIELD_TEXT, mt: "8px" }}>
          {message}
        </Box>
      )}
      {hint === undefined ? null : (
        <Box id={hintId} sx={{ ...textStyle("hint"), color: "var(--dd-muted)", mt: "8px" }}>
          {hint}
        </Box>
      )}
    </Box>
  );
}
