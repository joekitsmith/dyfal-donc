import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { apiClient } from "@/api/client";
import { browserStorage } from "@/utils/safe-storage";

import { LEARNER_QUERY_KEY } from "../constants";
import { createLearner, resolveLearner } from "./resolve-learner";

export function useLearner() {
  const queryClient = useQueryClient();
  const learner = useQuery({
    queryFn: () => resolveLearner(apiClient, browserStorage),
    queryKey: LEARNER_QUERY_KEY,
  });
  const startOver = useMutation({
    mutationFn: () => createLearner(apiClient, browserStorage),
    onSuccess: (learnerId) => {
      queryClient.setQueryData(LEARNER_QUERY_KEY, learnerId);
    },
  });

  return {
    error: learner.error ?? startOver.error,
    isLoading: learner.isPending,
    learnerId: learner.data,
    startOver: startOver.mutate,
  };
}
