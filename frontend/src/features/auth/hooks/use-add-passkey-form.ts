import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { MAXIMUM_LABEL_LENGTH } from "../constants";
import { useSaveProgress } from "./use-save-progress";

const schema = z.object({ label: z.string().trim().max(MAXIMUM_LABEL_LENGTH) });

type Values = z.infer<typeof schema>;

/** The form that adds another passkey, with an optional name for it. */
export function useAddPasskeyForm() {
  const { formState, handleSubmit, register, reset } = useForm<Values>({
    defaultValues: { label: "" },
    resolver: zodResolver(schema),
  });
  const { failure, isSaving, save } = useSaveProgress(() => {
    reset();
  });

  return {
    failure,
    field: {
      error: formState.errors.label !== undefined,
      helperText: formState.errors.label?.message ?? "Optional: a name to tell your passkeys apart",
      register: register("label"),
    },
    isSaving,
    onSubmit: handleSubmit(({ label }) => {
      save(label === "" ? undefined : label);
    }),
  };
}
