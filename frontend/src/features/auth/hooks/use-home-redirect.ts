import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { ROUTES } from "@/config/paths";

import { useSession } from "../api/use-session";

/** Sends people where they belong once it is known who is signed in: the lesson, or the welcome screen. */
export function useHomeRedirect() {
  const router = useRouter();
  const { data } = useSession();

  useEffect(() => {
    if (data !== undefined) {
      router.replace(data === null ? ROUTES.welcome : ROUTES.learn);
    }
  }, [data, router]);
}
