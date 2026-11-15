import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";

import { useAddPasskeyForm } from "../hooks/use-add-passkey-form";
import { PasskeyFailureAlert } from "./passkey-failure-alert";

export function AddPasskeyForm() {
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
        Add another passkey
      </Button>
      {failure ? <PasskeyFailureAlert failure={failure} /> : null}
    </Stack>
  );
}
