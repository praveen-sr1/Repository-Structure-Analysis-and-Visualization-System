import { Folder, RefreshCw, Trash2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import {
  useDeleteRepository,
  useRepositories,
  useRescanRepository,
} from "@/hooks/useRepositories";
import { cn } from "@/lib/utils";
import { useUiStore } from "@/stores/uiStore";
import { formatDate } from "@/utils/format";

/** Lists analysed repositories and lets the user switch, rescan, or delete. */
export function RepoExplorer() {
  const { data, isLoading } = useRepositories();
  const activeRepositoryId = useUiStore((s) => s.activeRepositoryId);
  const setActiveRepository = useUiStore((s) => s.setActiveRepository);
  const rescan = useRescanRepository();
  const remove = useDeleteRepository();

  if (isLoading) {
    return (
      <div className="space-y-2">
        {Array.from({ length: 3 }).map((_, i) => (
          <Skeleton key={i} className="h-12 w-full" />
        ))}
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <p className="px-1 py-2 text-sm text-muted-foreground">
        No repositories yet. Scan one to get started.
      </p>
    );
  }

  return (
    <ul className="space-y-1">
      {data.map((repo) => {
        const isActive = repo.id === activeRepositoryId;
        return (
          <li key={repo.id}>
            <div
              className={cn(
                "group flex items-center gap-2 rounded-md border px-2.5 py-2 transition-colors",
                isActive
                  ? "border-primary/50 bg-primary/10"
                  : "border-transparent hover:bg-accent",
              )}
            >
              <button
                type="button"
                onClick={() => setActiveRepository(repo.id)}
                className="flex min-w-0 flex-1 items-center gap-2 text-left"
              >
                <Folder
                  className={cn(
                    "size-4 shrink-0",
                    isActive ? "text-primary" : "text-muted-foreground",
                  )}
                />
                <span className="min-w-0">
                  <span className="block truncate text-sm font-medium">
                    {repo.name}
                  </span>
                  <span className="block truncate text-xs text-muted-foreground">
                    {repo.total_files} files · {formatDate(repo.last_scanned_at)}
                  </span>
                </span>
              </button>
              <div className="flex shrink-0 items-center opacity-0 transition-opacity group-hover:opacity-100">
                <Button
                  variant="ghost"
                  size="icon"
                  className="size-7"
                  aria-label="Rescan repository"
                  disabled={rescan.isPending}
                  onClick={() => rescan.mutate(repo.id)}
                >
                  <RefreshCw className="size-3.5" />
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  className="size-7 text-muted-foreground hover:text-destructive"
                  aria-label="Delete repository"
                  disabled={remove.isPending}
                  onClick={() => {
                    remove.mutate(repo.id);
                    if (isActive) setActiveRepository(null);
                  }}
                >
                  <Trash2 className="size-3.5" />
                </Button>
              </div>
            </div>
          </li>
        );
      })}
    </ul>
  );
}
