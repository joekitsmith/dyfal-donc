"use client";

import Typography from "@mui/material/Typography";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { ROUTES } from "@/config/paths";
import { useSession } from "@/features/auth";

/** For now the home screen only sends people where they belong: the lesson, or the welcome screen. */
export function HomePage() {
  const router = useRouter();
  const { data } = useSession();

  useEffect(() => {
    if (data !== undefined) {
      router.replace(data === null ? ROUTES.welcome : ROUTES.learn);
    }
  }, [data, router]);

  return <Typography>Loading</Typography>;
}
