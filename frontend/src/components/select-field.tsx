import Box from "@mui/material/Box";
import { useId } from "react";
import { type UseFormRegisterReturn } from "react-hook-form";

import { ChevronIcon } from "./icons/chevron-icon";

type SelectFieldProps = {
  readonly input: UseFormRegisterReturn;
  readonly label: string;
  /** Why the field is not right. It is announced when it appears. */
  readonly message?: string | undefined;
  readonly options: readonly { readonly label: string; readonly value: string }[];
  /** The first option, which stands for nothing having been chosen. */
  readonly prompt: string;
};

const FIELD_TEXT = { fontSize: "0.9375rem", fontWeight: 500 } as const;
const SELECT_HEIGHT = 56;

/** A native select in the box a text field has. */
export function SelectField({ input, label, message, options, prompt }: SelectFieldProps) {
  const selectId = useId();
  const messageId = useId();

  return (
    <Box>
      <Box component="label" htmlFor={selectId} sx={{ ...FIELD_TEXT, display: "block", mb: "6px" }}>
        {label}
      </Box>
      <Box sx={{ position: "relative" }}>
        <Box
          aria-describedby={message === undefined ? undefined : messageId}
          aria-invalid={message === undefined ? undefined : true}
          component="select"
          id={selectId}
          {...input}
          sx={{
            appearance: "none",
            backgroundColor: "var(--dd-surface)",
            border: `2px solid ${message === undefined ? "var(--dd-line)" : "var(--dd-ink)"}`,
            borderRadius: "10px",
            boxSizing: "border-box",
            color: "var(--dd-ink)",
            display: "block",
            fontSize: "1.0625rem",
            height: SELECT_HEIGHT,
            pl: "14px",
            pr: "44px",
            width: "100%",
          }}
        >
          <option value="">{prompt}</option>
          {options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </Box>
        <Box
          aria-hidden="true"
          sx={{
            display: "flex",
            pointerEvents: "none",
            position: "absolute",
            right: "14px",
            top: "50%",
            transform: "translateY(-50%)",
          }}
        >
          <ChevronIcon direction="down" size={20} />
        </Box>
      </Box>
      {message === undefined ? null : (
        <Box id={messageId} role="alert" sx={{ ...FIELD_TEXT, mt: "8px" }}>
          {message}
        </Box>
      )}
    </Box>
  );
}
