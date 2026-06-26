import { memo } from "react";
import { Handle, Position, type NodeProps } from "reactflow";

import { cn } from "@/lib/utils";
import { useGraphStore } from "@/stores/graphStore";
import { useUiStore } from "@/stores/uiStore";
import { complexityBand } from "@/utils/format";
import type { FileNodeData } from "@/utils/graphTransform";

/** Custom React Flow node rendering a file with language accent + metrics. */
function FileNodeComponent({ id, data }: NodeProps<FileNodeData>) {
  const selectedNodeId = useUiStore((s) => s.selectedNodeId);
  const highlightedNodes = useGraphStore((s) => s.highlightedNodes);

  const isSelected = selectedNodeId === id;
  const hasSelection = selectedNodeId !== null;
  const isHighlighted = highlightedNodes.has(id);
  const isDimmed = hasSelection && !isHighlighted;

  const band = complexityBand(data.complexity);

  return (
    <div
      className={cn(
        "group min-w-[180px] max-w-[220px] rounded-lg border bg-card px-3 py-2 shadow-sm transition-all",
        isSelected
          ? "border-primary ring-2 ring-primary/40"
          : "border-border hover:border-primary/50",
        isDimmed && "opacity-30",
      )}
    >
      <Handle
        type="target"
        position={Position.Left}
        className="!h-2 !w-2 !border-border !bg-muted-foreground"
      />
      <div className="flex items-center gap-2">
        <span
          className="size-2.5 shrink-0 rounded-full"
          style={{ backgroundColor: data.color }}
        />
        <span className="truncate text-sm font-medium" title={data.path}>
          {data.label}
        </span>
      </div>
      <div className="mt-1.5 flex items-center justify-between text-[11px] text-muted-foreground">
        <span>{data.loc} LOC</span>
        <span className={band.className} title={`Complexity: ${data.complexity}`}>
          CC {data.complexity}
        </span>
      </div>
      <Handle
        type="source"
        position={Position.Right}
        className="!h-2 !w-2 !border-border !bg-muted-foreground"
      />
    </div>
  );
}

export const FileNode = memo(FileNodeComponent);
