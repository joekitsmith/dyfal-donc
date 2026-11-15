/** The day the learner met an item, such as "3 March 2026". */
export function formatFirstMet(moment: string): string {
  return new Date(moment).toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric" });
}
