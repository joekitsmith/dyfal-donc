import Box from "@mui/material/Box";

import { Button } from "@/components/button";
import { TextField } from "@/components/text-field";
import { textStyle } from "@/theme/text-style";

import { useAddPasskeyForm } from "../hooks/use-add-passkey-form";
import { PasskeyFailureNotice } from "./passkey-failure-notice";

type AddPasskeyFormProps = {
  readonly label: string;
  readonly placeholder?: string | undefined;
  readonly submit: { readonly label: string; readonly variant: "primary" | "quiet" };
};

export function AddPasskeyForm({ label, placeholder, submit }: AddPasskeyFormProps) {
  const { failure, field, isSaving, onSubmit } = useAddPasskeyForm();

  return (
    <Box
      component="form"
      noValidate
      onSubmit={(event) => {
        void onSubmit(event);
      }}
    >
      <TextField input={field.register} label={label} message={field.message} placeholder={placeholder} />
      <Box sx={{ mt: "24px" }}>
        <Button type="submit" unavailable={isSaving} variant={submit.variant}>
          {submit.label}
        </Button>
      </Box>
      <Box sx={{ ...textStyle("hint"), color: "var(--dd-muted)", mt: "8px" }}>Your device will ask you to confirm.</Box>
      {failure ? (
        <Box sx={{ mt: "12px" }}>
          <PasskeyFailureNotice failure={failure} />
        </Box>
      ) : null}
    </Box>
  );
}
