import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { ApiError } from "@/api/api-error";
import { ROUTES } from "@/config/paths";

import { useSession } from "../api/use-session";
import { useSignInWithRecoveryCode } from "../api/use-sign-in-with-recovery-code";
import {
  BAD_REQUEST_STATUS,
  MAXIMUM_CODE_LENGTH,
  RECOVERY_CODE_EMPTY_MESSAGE,
  RECOVERY_CODE_FAILED_MESSAGE,
  RECOVERY_CODE_NOT_RECOGNISED_MESSAGE,
} from "../constants";

const schema = z.object({ code: z.string().trim().min(1, RECOVERY_CODE_EMPTY_MESSAGE).max(MAXIMUM_CODE_LENGTH) });

type Values = z.infer<typeof schema>;

/**
 * What the recovery screen does: sign in with a code, then stay to add a new passkey. Someone who
 * is already signed in, and did not just use a code, is sent on to Home.
 */
export function useRecover() {
  const router = useRouter();
  const session = useSession();
  const signIn = useSignInWithRecoveryCode();
  const { formState, handleSubmit, register } = useForm<Values>({
    defaultValues: { code: "" },
    resolver: zodResolver(schema),
  });
  const alreadySignedIn = session.data !== undefined && session.data !== null && !signIn.isSuccess;

  useEffect(() => {
    if (alreadySignedIn) {
      router.replace(ROUTES.home);
    }
  }, [alreadySignedIn, router]);

  const failure = signIn.isError
    ? signIn.error instanceof ApiError && signIn.error.status === BAD_REQUEST_STATUS
      ? RECOVERY_CODE_NOT_RECOGNISED_MESSAGE
      : RECOVERY_CODE_FAILED_MESSAGE
    : undefined;

  return {
    field: {
      message: formState.errors.code?.message ?? failure,
      register: register("code"),
    },
    isLoading: session.isPending || alreadySignedIn,
    isSigningIn: signIn.isPending,
    onSubmit: handleSubmit(({ code }) => {
      signIn.mutate(code);
    }),
    recovered: signIn.isSuccess,
  };
}
