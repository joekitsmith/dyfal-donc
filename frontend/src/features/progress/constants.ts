export function progressQueryKey(learnerId: string) {
  return ["progress", learnerId] as const;
}
