export const COURSE_QUERY_KEY = ["course"] as const;

export function itemQueryKey(itemId: string) {
  return ["course-item", itemId] as const;
}

export const NOT_FOUND_STATUS = 404;
