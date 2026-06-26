import { FileCode2, X } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/common/EmptyState";
import { AiExplanationPanel } from "@/components/panels/AiExplanationPanel";
import { MetricsPanel } from "@/components/panels/MetricsPanel";
import { useGraph } from "@/hooks/useGraph";
import { useUiStore } from "@/stores/uiStore";
import { languageLabel } from "@/utils/format";

/** Right-hand details panel: file identity, metrics, and AI explanation. */
export function FileDetailsPanel() {
  const repositoryId = useUiStore((s) => s.activeRepositoryId);
  const selectedNodeId = useUiStore((s) => s.selectedNodeId);
  const selectNode = useUiStore((s) => s.selectNode);

  const { data: graph } = useGraph(repositoryId);

  if (repositoryId === null || !selectedNodeId) {
    return (
      <EmptyState
        title="No file selected"
        message="Click a node in the graph to inspect its metrics and AI explanation."
      />
    );
  }

  const node = graph?.nodes.find((n) => n.id === selectedNodeId);
  const fileName = node?.label ?? selectedNodeId;
  const language = node?.language ?? "unknown";

  return (
    <div className="flex h-full flex-col">
      {/* Header */}
      <div className="flex items-start justify-between gap-2 border-b border-border p-4">
        <div className="flex min-w-0 items-start gap-2">
          <FileCode2 className="mt-0.5 size-5 shrink-0 text-primary" />
          <div className="min-w-0">
            <h2 className="truncate font-semibold" title={fileName}>
              {fileName}
            </h2>
            <p
              className="truncate text-xs text-muted-foreground"
              title={selectedNodeId}
            >
              {selectedNodeId}
            </p>
          </div>
        </div>
        <Button
          variant="ghost"
          size="icon"
          onClick={() => selectNode(null)}
          aria-label="Close details"
        >
          <X />
        </Button>
      </div>

      <div className="flex-1 space-y-6 overflow-y-auto p-4">
        <div>
          <Badge style={{ borderColor: "transparent" }} variant="secondary">
            {languageLabel(language)}
          </Badge>
        </div>

        <section>
          <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
            Metrics
          </h3>
          <MetricsPanel repositoryId={repositoryId} filePath={selectedNodeId} />
        </section>

        <section>
          <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
            Explanation
          </h3>
          <AiExplanationPanel
            repositoryId={repositoryId}
            filePath={selectedNodeId}
          />
        </section>
      </div>
    </div>
  );
}
