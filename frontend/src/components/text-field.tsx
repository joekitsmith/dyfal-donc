import type { ComponentPropsWithRef } from "react";

import Box from "@mui/material/Box";
import { useId } from "react";

import { textStyle } from "@/theme/text-style";

type TextFieldProps = {
  /** The field takes a code, so its text is larger and spaced out. */
  readonly code?: boolean;
  readonly hint?: string;
  /** Attributes for the input itself, which is where a form library puts what it registers. */
  readonly input: ComponentPropsWithRef<"input">;
  readonly label: string;
  /** Why the field is not right. It is announced when it appears. */
  readonly message?: string | undefined;
  readonly placeholder?: string | undefined;
};

const FIELD_TEXT = { fontSize: "0.9375rem", fontWeight: 500 } as const;
const INPUT_HEIGHT = 56;

export function TextField({ code = false, hint, input, label, message, placeholder }: TextFieldProps) {
  const inputId = useId();
  const messageId = useId();
  const hintId = useId();
  const describedBy = [message === undefined ? null : messageId, hint === undefined ? null : hintId]
    .filter((identifier) => identifier !== null)
    .join(" ");

  return (
    <Box>
      <Box component="label" htmlFor={inputId} sx={{ ...FIELD_TEXT, display: "block", mb: "6px" }}>
        {label}
      </Box>
      <Box
        aria-describedby={describedBy === "" ? undefined : describedBy}
        aria-invalid={message === undefined ? undefined : true}
        component="input"
        id={inputId}
        placeholder={placeholder}
        {...input}
        sx={{
          ...(code ? { fontSize: "1.1875rem", letterSpacing: "0.04em" } : { fontSize: "1.0625rem" }),
          "&::placeholder": { color: "var(--dd-muted)", opacity: 1 },
          backgroundColor: "var(--dd-surface)",
          border: `2px solid ${message === undefined ? "var(--dd-line)" : "var(--dd-ink)"}`,
          borderRadius: "10px",
          boxSizing: "border-box",
          color: "var(--dd-ink)",
          height: INPUT_HEIGHT,
          px: "14px",
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
