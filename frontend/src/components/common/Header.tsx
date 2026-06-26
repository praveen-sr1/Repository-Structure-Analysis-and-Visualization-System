import { Network, PanelLeft } from "lucide-react";

import { Button } from "@/components/ui/button";
import { SearchBar } from "@/components/common/SearchBar";
import { ThemeToggle } from "@/components/common/ThemeToggle";
import { useUiStore } from "@/stores/uiStore";

/** Top application bar: brand, sidebar toggle, search, theme. */
export function Header() {
  const toggleSidebar = useUiStore((s) => s.toggleSidebar);
  const activeRepositoryId = useUiStore((s) => s.activeRepositoryId);

  return (
    <header className="flex h-14 shrink-0 items-center gap-3 border-b border-border bg-card/60 px-3 backdrop-blur">
      <Button
        variant="ghost"
        size="icon"
        onClick={toggleSidebar}
        aria-label="Toggle sidebar"
      >
        <PanelLeft />
      </Button>

      <div className="flex items-center gap-2">
        <div className="flex size-7 items-center justify-center rounded-md bg-primary/15 text-primary">
          <Network className="size-4" />
        </div>
        <span className="font-semibold tracking-tight">Repo Analyzer</span>
      </div>

      <div className="ml-auto flex items-center gap-2">
        {activeRepositoryId !== null && <SearchBar className="w-64" />}
        <ThemeToggle />
      </div>
    </header>
  );
}
