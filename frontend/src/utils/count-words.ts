/** Words as the think time counts them: the pieces between spaces. */
export function countWords(sentence: string): number {
  return sentence.split(/\s+/).filter((word) => word !== "").length;
}
