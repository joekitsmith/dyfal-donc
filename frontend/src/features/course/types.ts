import type { components } from "@/api/schema";

export type CourseItem = components["schemas"]["ItemResponse"];
export type CourseProgress = components["schemas"]["CourseProgressResponse"];
export type ItemDetail = components["schemas"]["ItemDetailResponse"];
export type TopicProgress = components["schemas"]["TopicProgressResponse"];

/** An item the learner has met that matched a search, with the topic it belongs to. */
export type SearchResult = {
  readonly item: CourseItem;
  readonly topic: string;
};
