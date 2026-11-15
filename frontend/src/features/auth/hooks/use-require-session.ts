import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { ROUTES } from "@/config/paths";

import { useSession } from "../api/use-session";

/** The signed-in user, or a move to the welcome screen when nobody is. The user is undefined until known. */
export function useRequireSession() {
  const router = useRouter();
  const { data, error } = useSession();

  useEffect(() => {
    if (data === null) {
      router.replace(ROUTES.welcome);
    }
  }, [data, router]);

  return { error, user: data ?? undefined };
}
