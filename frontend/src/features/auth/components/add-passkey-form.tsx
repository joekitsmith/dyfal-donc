import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";

import { useAddPasskeyForm } from "../hooks/use-add-passkey-form";
import { PasskeyFailureAlert } from "./passkey-failure-alert";

type AddPasskeyFormProps = {
  readonly submitLabel: string;
};

export function AddPasskeyForm({ submitLabel }: AddPasskeyFormProps) {
  const { failure, field, isSaving, onSubmit } = useAddPasskeyForm();

  return (
    <Stack
      component="form"
      noValidate
      onSubmit={(event) => {
        void onSubmit(event);
      }}
      spacing={1}
    >
      <TextField error={field.error} helperText={field.helperText} label="Name" size="small" {...field.register} />
      <Button disabled={isSaving} type="submit" variant="outlined">
        {submitLabel}
      </Button>
      {failure ? <PasskeyFailureAlert failure={failure} /> : null}
    </Stack>
  );
}
