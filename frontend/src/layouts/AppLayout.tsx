import { useState } from "react";
import { ReactFlowProvider } from "reactflow";

import { Header } from "@/components/common/Header";
import { Sidebar } from "@/components/sidebar/Sidebar";
import { ScanDialog } from "@/components/common/ScanDialog";
import { FileDetailsPanel } from "@/components/panels/FileDetailsPanel";
import { DependencyGraph } from "@/components/graph/DependencyGraph";
import { useUiStore } from "@/stores/uiStore";

/** Three-pane IDE-style layout: sidebar · graph canvas · details panel. */
export function AppLayout() {
  const [scanOpen, setScanOpen] = useState(false);
  const selectedNodeId = useUiStore((s) => s.selectedNodeId);

  return (
    <div className="flex h-screen w-screen flex-col overflow-hidden bg-background text-foreground">
      <Header />

      <div className="flex min-h-0 flex-1">
        <Sidebar onOpenScan={() => setScanOpen(true)} />

        <main className="relative min-w-0 flex-1">
          <ReactFlowProvider>
            <DependencyGraph onOpenScan={() => setScanOpen(true)} />
          </ReactFlowProvider>
        </main>

        {/* Details panel slides in when a node is selected. */}
        <aside
          className={
            selectedNodeId
              ? "w-[360px] shrink-0 border-l border-border bg-card/40"
              : "hidden"
          }
        >
          <FileDetailsPanel />
        </aside>
      </div>

      <ScanDialog open={scanOpen} onClose={() => setScanOpen(false)} />
    </div>
  );
}
