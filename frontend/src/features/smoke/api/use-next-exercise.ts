import { queryApi } from "@/api/client";

export function useNextExercise(learnerId: string) {
  const mutation = queryApi.useMutation("get", "/learners/{learner_id}/next");

  return {
    error: mutation.error,
    fetchNext: () => {
      mutation.mutate({ params: { path: { learner_id: learnerId } } });
    },
    isPending: mutation.isPending,
    outcome: mutation.data,
  };
}
