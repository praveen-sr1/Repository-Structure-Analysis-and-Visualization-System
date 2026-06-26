import { useQuery } from "@tanstack/react-query";

import { api } from "@/services/api";

/**
 * Fetch the AI summary for a file.
 *
 * Summaries are cached server-side by content hash, so this query is cheap to
 * keep around. It only runs when a file is actually selected.
 */
export function useSummary(repositoryId: number | null, path: string | null) {
  return useQuery({
    queryKey: ["summary", repositoryId, path],
    queryFn: () => api.getFileSummary(repositoryId as number, path as string),
    enabled: repositoryId !== null && !!path,
    staleTime: 5 * 60_000,
  });
}
