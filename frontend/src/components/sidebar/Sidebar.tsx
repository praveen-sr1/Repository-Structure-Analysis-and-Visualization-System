import { Plus } from "lucide-react";

import { Button } from "@/components/ui/button";
import { RepoExplorer } from "@/components/sidebar/RepoExplorer";
import { StatsSummary } from "@/components/sidebar/StatsSummary";
import { cn } from "@/lib/utils";
import { useUiStore } from "@/stores/uiStore";

interface SidebarProps {
  onOpenScan: () => void;
}

/** Left sidebar: repository explorer + active-repo statistics. */
export function Sidebar({ onOpenScan }: SidebarProps) {
  const sidebarOpen = useUiStore((s) => s.sidebarOpen);
  const activeRepositoryId = useUiStore((s) => s.activeRepositoryId);

  return (
    <aside
      className={cn(
        "flex h-full shrink-0 flex-col border-r border-border bg-card/40 transition-all duration-200",
        sidebarOpen ? "w-72" : "w-0 overflow-hidden",
      )}
    >
      <div className="flex items-center justify-between gap-2 border-b border-border p-3">
        <h2 className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
          Repositories
        </h2>
        <Button size="sm" onClick={onOpenScan}>
          <Plus className="size-4" />
          Scan
        </Button>
      </div>

      <div className="flex-1 space-y-6 overflow-y-auto p-3">
        <RepoExplorer />
        {activeRepositoryId !== null && (
          <section>
            <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              Overview
            </h3>
            <StatsSummary repositoryId={activeRepositoryId} />
          </section>
        )}
      </div>
    </aside>
  );
}
