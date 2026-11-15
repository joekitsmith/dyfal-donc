import { useQuery } from "@tanstack/react-query";

import { apiClient } from "@/api/client";

import { SETTINGS_QUERY_KEY } from "../constants";
import { getSettings } from "./settings-requests";

export function useSettings() {
  return useQuery({ queryFn: () => getSettings(apiClient), queryKey: SETTINGS_QUERY_KEY });
}
