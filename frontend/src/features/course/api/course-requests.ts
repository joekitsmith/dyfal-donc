import type { ApiClient } from "@/api/client";

import { unwrap } from "@/api/api-error";

import type { CourseProgress, ItemDetail } from "../types";

export async function getCourse(client: ApiClient): Promise<CourseProgress> {
  return unwrap(await client.GET("/me/course"));
}

export async function getItem(client: ApiClient, itemId: string): Promise<ItemDetail> {
  return unwrap(await client.GET("/me/items/{item_id}", { params: { path: { item_id: itemId } } }));
}
