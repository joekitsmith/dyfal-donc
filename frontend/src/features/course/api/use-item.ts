import { useQuery } from "@tanstack/react-query";

import { apiClient } from "@/api/client";

import { itemQueryKey } from "../constants";
import { getItem } from "./course-requests";

export function useItem(itemId: string) {
  return useQuery({
    queryFn: () => getItem(apiClient, itemId),
    queryKey: itemQueryKey(itemId),
    refetchOnMount: "always",
  });
}
