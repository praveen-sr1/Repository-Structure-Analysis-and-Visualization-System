import { useQuery } from "@tanstack/react-query";

import { api } from "@/services/api";

/** Fetch the dependency graph for a repository. */
export function useGraph(repositoryId: number | null) {
  return useQuery({
    queryKey: ["graph", repositoryId],
    queryFn: () => api.getGraph(repositoryId as number),
    enabled: repositoryId !== null,
  });
}

/** Fetch aggregate statistics for a repository. */
export function useStats(repositoryId: number | null) {
  return useQuery({
    queryKey: ["stats", repositoryId],
    queryFn: () => api.getStats(repositoryId as number),
    enabled: repositoryId !== null,
  });
}
