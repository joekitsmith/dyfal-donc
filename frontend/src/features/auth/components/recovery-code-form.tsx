import type { ComponentPropsWithRef, SubmitEvent } from "react";

import Box from "@mui/material/Box";

import { Button } from "@/components/button";
import { TextField } from "@/components/text-field";

type RecoveryCodeFormProps = {
  readonly field: { readonly message: string | undefined; readonly register: ComponentPropsWithRef<"input"> };
  readonly isSigningIn: boolean;
  readonly onSubmit: (event: SubmitEvent<HTMLFormElement>) => Promise<void>;
};

export function RecoveryCodeForm({ field, isSigningIn, onSubmit }: RecoveryCodeFormProps) {
  return (
    <Box
      component="form"
      noValidate
      onSubmit={(event) => {
        void onSubmit(event);
      }}
      sx={{ mt: "28px" }}
    >
      <TextField
        code
        hint="Dashes, spaces and capitals don't matter."
        input={{ ...field.register, autoCapitalize: "characters", autoComplete: "off", spellCheck: false }}
        label="Recovery code"
        message={field.message}
      />
      <Box sx={{ mt: "24px" }}>
        <Button type="submit" unavailable={isSigningIn} variant="primary">
          {isSigningIn ? "Signing in…" : "Sign in"}
        </Button>
      </Box>
    </Box>
  );
}
