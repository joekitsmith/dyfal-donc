import useMediaQuery from "@mui/material/useMediaQuery";

import { MEDIA } from "@/theme/tokens";

/** Whether the person has asked their device for less movement. */
export function usePrefersReducedMotion(): boolean {
  return useMediaQuery(MEDIA.reducedMotion.replace("@media ", ""), { noSsr: true });
}
