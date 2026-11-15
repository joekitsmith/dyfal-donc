import { zodResolver } from "@hookform/resolvers/zod";
import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { MAXIMUM_LABEL_LENGTH } from "../constants";
import { useSaveProgress } from "../hooks/use-save-progress";
import { PasskeyFailureAlert } from "./passkey-failure-alert";

const schema = z.object({ label: z.string().trim().max(MAXIMUM_LABEL_LENGTH) });

type Values = z.infer<typeof schema>;

export function AddPasskeyForm() {
  const { formState, handleSubmit, register, reset } = useForm<Values>({
    defaultValues: { label: "" },
    resolver: zodResolver(schema),
  });
  const { failure, isSaving, save } = useSaveProgress(() => {
    reset();
  });

  return (
    <Stack
      component="form"
      noValidate
      onSubmit={(event) => {
        void handleSubmit(({ label }) => {
          save(label === "" ? undefined : label);
        })(event);
      }}
      spacing={1}
    >
      <TextField
        error={formState.errors.label !== undefined}
        helperText={formState.errors.label?.message ?? "Optional: a name to tell your passkeys apart"}
        label="Name"
        size="small"
        {...register("label")}
      />
      <Button disabled={isSaving} type="submit" variant="outlined">
        Add another passkey
      </Button>
      {failure ? <PasskeyFailureAlert failure={failure} /> : null}
    </Stack>
  );
}
