import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { api, ApiError } from "@/services/api";
import type { ScanRequest } from "@/types";

/** List all analysed repositories. */
export function useRepositories() {
  return useQuery({
    queryKey: ["repositories"],
    queryFn: api.listRepositories,
  });
}

/** Scan a new repository (or refresh an existing one by path). */
export function useScanRepository() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: ScanRequest) => api.scanRepository(payload),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["repositories"] });
      toast.success(
        `Scanned “${data.repository.name}” — ${data.nodes_created} files, ${data.edges_created} dependencies.`,
      );
    },
    onError: (error: ApiError) => {
      toast.error(error.message || "Failed to scan repository.");
    },
  });
}

/** Re-run analysis for an existing repository. */
export function useRescanRepository() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => api.rescanRepository(id),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["repositories"] });
      queryClient.invalidateQueries({
        queryKey: ["graph", data.repository.id],
      });
      queryClient.invalidateQueries({
        queryKey: ["stats", data.repository.id],
      });
      toast.success(`Rescanned “${data.repository.name}”.`);
    },
    onError: (error: ApiError) => {
      toast.error(error.message || "Failed to rescan repository.");
    },
  });
}

/** Delete a repository. */
export function useDeleteRepository() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => api.deleteRepository(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["repositories"] });
      toast.success("Repository removed.");
    },
    onError: (error: ApiError) => {
      toast.error(error.message || "Failed to delete repository.");
    },
  });
}
