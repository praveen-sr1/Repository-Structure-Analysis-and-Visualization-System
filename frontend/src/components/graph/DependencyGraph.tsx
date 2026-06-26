import { useCallback, useEffect, useMemo } from "react";
import ReactFlow, {
  Background,
  BackgroundVariant,
  Controls,
  MiniMap,
  useEdgesState,
  useNodesState,
  type Node,
  type NodeMouseHandler,
} from "reactflow";

import { ErrorState } from "@/components/common/ErrorState";
import { EmptyState } from "@/components/common/EmptyState";
import { GraphSkeleton } from "@/components/graph/GraphSkeleton";
import { FileNode } from "@/components/graph/FileNode";
import { useGraph } from "@/hooks/useGraph";
import { useGraphStore } from "@/stores/graphStore";
import { useUiStore } from "@/stores/uiStore";
import { languageColor } from "@/utils/format";
import {
  toFlowEdges,
  toFlowNodes,
  type FileNodeData,
} from "@/utils/graphTransform";

const nodeTypes = { fileNode: FileNode };

interface DependencyGraphProps {
  onOpenScan: () => void;
}

/** The interactive React Flow dependency-graph canvas. */
export function DependencyGraph({ onOpenScan }: DependencyGraphProps) {
  const repositoryId = useUiStore((s) => s.activeRepositoryId);
  const selectedNodeId = useUiStore((s) => s.selectedNodeId);
  const selectNode = useUiStore((s) => s.selectNode);
  const searchQuery = useUiStore((s) => s.searchQuery);

  const computeHighlights = useGraphStore((s) => s.computeHighlights);
  const highlightedEdges = useGraphStore((s) => s.highlightedEdges);

  const { data, isLoading, isError, refetch } = useGraph(repositoryId);

  const [nodes, setNodes, onNodesChange] = useNodesState<FileNodeData>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  // Rebuild flow nodes/edges whenever the graph payload changes.
  useEffect(() => {
    if (!data) return;
    setNodes(toFlowNodes(data.nodes, data.edges));
    setEdges(toFlowEdges(data.edges, new Set(), false));
  }, [data, setNodes, setEdges]);

  // Recompute highlight sets when the selection or graph changes.
  useEffect(() => {
    if (!data) return;
    computeHighlights(selectedNodeId, data.edges);
  }, [selectedNodeId, data, computeHighlights]);

  // Restyle edges when highlights change.
  useEffect(() => {
    if (!data) return;
    setEdges(toFlowEdges(data.edges, highlightedEdges, selectedNodeId !== null));
  }, [data, highlightedEdges, selectedNodeId, setEdges]);

  // Apply search dimming to nodes.
  const displayedNodes = useMemo(() => {
    if (!searchQuery.trim()) return nodes;
    const q = searchQuery.toLowerCase();
    return nodes.map((n) => {
      const matches =
        n.data.label.toLowerCase().includes(q) ||
        n.data.path.toLowerCase().includes(q);
      return {
        ...n,
        style: { ...n.style, opacity: matches ? 1 : 0.2 },
      };
    });
  }, [nodes, searchQuery]);

  const onNodeClick: NodeMouseHandler = useCallback(
    (_, node) => {
      selectNode(node.id === selectedNodeId ? null : node.id);
    },
    [selectNode, selectedNodeId],
  );

  const onPaneClick = useCallback(() => selectNode(null), [selectNode]);

  if (repositoryId === null) {
    return (
      <EmptyState
        title="No repository selected"
        message="Scan a local repository to visualise its dependency graph."
        actionLabel="Scan a repository"
        onAction={onOpenScan}
      />
    );
  }
  if (isLoading) return <GraphSkeleton />;
  if (isError)
    return (
      <ErrorState
        title="Could not load the graph"
        message="The dependency graph failed to load."
        onRetry={() => refetch()}
      />
    );
  if (data && data.nodes.length === 0) {
    return (
      <EmptyState
        title="No analysable files found"
        message="This repository has no supported source files to graph."
      />
    );
  }

  return (
    <ReactFlow
      nodes={displayedNodes}
      edges={edges}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      onNodeClick={onNodeClick}
      onPaneClick={onPaneClick}
      nodeTypes={nodeTypes}
      fitView
      minZoom={0.1}
      maxZoom={2}
      proOptions={{ hideAttribution: true }}
    >
      <Background variant={BackgroundVariant.Dots} gap={20} size={1} />
      <Controls className="rounded-md border border-border" />
      <MiniMap
        pannable
        zoomable
        nodeColor={(n: Node<FileNodeData>) =>
          languageColor(n.data?.language ?? "unknown")
        }
        maskColor="hsl(var(--background) / 0.6)"
      />
    </ReactFlow>
  );
}
