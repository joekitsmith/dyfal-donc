import { z } from "zod";

import { CATEGORY_OPTIONS, DESCRIPTION_MAXIMUM_LENGTH } from "../constants";

export const reportSchema = z.object({
  category: z.string().pipe(
    z.enum(
      CATEGORY_OPTIONS.map((option) => option.value),
      "Choose what kind of problem it is",
    ),
  ),
  description: z
    .string()
    .trim()
    .min(1, "Say what is wrong")
    .max(DESCRIPTION_MAXIMUM_LENGTH, `Use at most ${DESCRIPTION_MAXIMUM_LENGTH} characters`),
  subjectId: z.string(),
});
