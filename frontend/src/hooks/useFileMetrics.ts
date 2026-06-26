import { useQuery } from "@tanstack/react-query";

import { api } from "@/services/api";

/** Fetch detailed metrics for a single file. */
export function useFileMetrics(
  repositoryId: number | null,
  path: string | null,
) {
  return useQuery({
    queryKey: ["file-metrics", repositoryId, path],
    queryFn: () => api.getFileMetrics(repositoryId as number, path as string),
    enabled: repositoryId !== null && !!path,
  });
}
