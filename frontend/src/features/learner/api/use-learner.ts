import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { apiClient } from "@/api/client";

import { LEARNER_QUERY_KEY } from "../constants";
import { resolveLearner, startOver } from "./resolve-learner";

export function useLearner() {
  const queryClient = useQueryClient();
  const learner = useQuery({
    queryFn: () => resolveLearner(apiClient),
    queryKey: LEARNER_QUERY_KEY,
  });
  const startingOver = useMutation({
    mutationFn: () => startOver(apiClient),
    onSuccess: (learnerId) => {
      queryClient.setQueryData(LEARNER_QUERY_KEY, learnerId);
    },
  });

  return {
    error: learner.error ?? startingOver.error,
    isLoading: learner.isPending,
    learnerId: learner.data,
    startOver: startingOver.mutate,
  };
}
