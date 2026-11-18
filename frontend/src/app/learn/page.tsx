import { redirect } from "next/navigation";

import { ROUTES } from "@/config/paths";

export default function Page() {
  redirect(ROUTES.home);
}
