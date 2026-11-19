import { z } from "zod";

import { CATEGORY_OPTIONS, DESCRIPTION_MAXIMUM_LENGTH } from "../constants";

export const reportSchema = z.object({
  category: z.string().pipe(
    z.enum(
      CATEGORY_OPTIONS.map((option) => option.value),
      "Choose a kind of problem.",
    ),
  ),
  description: z
    .string()
    .trim()
    .min(1, "Say what is wrong.")
    .max(
      DESCRIPTION_MAXIMUM_LENGTH,
      `That's too long. Keep it under ${DESCRIPTION_MAXIMUM_LENGTH.toLocaleString("en-GB")} characters.`,
    ),
  subjectId: z.string(),
});
