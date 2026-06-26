/**
 * Graph transform & layout.
 *
 * Converts the backend graph payload into React Flow nodes/edges and assigns
 * each node a deterministic position. We use a lightweight layered layout
 * (rank by dependency depth, spread within each rank) to avoid pulling in a
 * heavy layout dependency while still producing a readable graph.
 */
import type { Edge, Node } from "reactflow";
import { MarkerType } from "reactflow";

import type { GraphEdge, GraphNode } from "@/types";
import { languageColor } from "./format";

export interface FileNodeData {
  label: string;
  path: string;
  language: string;
  loc: number;
  complexity: number;
  color: string;
}

const RANK_GAP_X = 280;
const NODE_GAP_Y = 90;

/** Assign each node a rank based on longest incoming dependency chain. */
function computeRanks(
  nodes: GraphNode[],
  edges: GraphEdge[],
): Map<string, number> {
  const incoming = new Map<string, string[]>();
  const outgoing = new Map<string, string[]>();
  for (const n of nodes) {
    incoming.set(n.id, []);
    outgoing.set(n.id, []);
  }
  for (const e of edges) {
    outgoing.get(e.source)?.push(e.target);
    incoming.get(e.target)?.push(e.source);
  }

  const rank = new Map<string, number>();
  const visiting = new Set<string>();

  // Longest-path rank via memoised DFS; cycles are broken defensively.
  const depth = (id: string): number => {
    if (rank.has(id)) return rank.get(id)!;
    if (visiting.has(id)) return 0; // cycle guard
    visiting.add(id);
    const parents = incoming.get(id) ?? [];
    const d = parents.length
      ? Math.max(...parents.map((p) => depth(p) + 1))
      : 0;
    visiting.delete(id);
    rank.set(id, d);
    return d;
  };

  for (const n of nodes) depth(n.id);
  return rank;
}

/** Build React Flow nodes with computed positions. */
export function toFlowNodes(
  nodes: GraphNode[],
  edges: GraphEdge[],
): Node<FileNodeData>[] {
  const ranks = computeRanks(nodes, edges);

  // Group node ids by rank to spread them vertically.
  const byRank = new Map<number, string[]>();
  for (const n of nodes) {
    const r = ranks.get(n.id) ?? 0;
    if (!byRank.has(r)) byRank.set(r, []);
    byRank.get(r)!.push(n.id);
  }

  const indexInRank = new Map<string, number>();
  for (const [, ids] of byRank) {
    ids.forEach((id, i) => indexInRank.set(id, i));
  }

  return nodes.map((n) => {
    const r = ranks.get(n.id) ?? 0;
    const i = indexInRank.get(n.id) ?? 0;
    const countInRank = byRank.get(r)?.length ?? 1;
    const offsetY = (i - (countInRank - 1) / 2) * NODE_GAP_Y;

    return {
      id: n.id,
      type: "fileNode",
      position: { x: r * RANK_GAP_X, y: offsetY + 400 },
      data: {
        label: n.label,
        path: n.path,
        language: n.language,
        loc: n.metrics.lines_of_code,
        complexity: n.metrics.cyclomatic_complexity,
        color: languageColor(n.language),
      },
    };
  });
}

/** Build React Flow edges, styling highlighted edges differently. */
export function toFlowEdges(
  edges: GraphEdge[],
  highlightedEdges: Set<string>,
  hasSelection: boolean,
): Edge[] {
  return edges.map((e) => {
    const highlighted = highlightedEdges.has(e.id);
    const dimmed = hasSelection && !highlighted;
    return {
      id: e.id,
      source: e.source,
      target: e.target,
      animated: highlighted,
      style: {
        stroke: highlighted ? "hsl(var(--primary))" : "hsl(var(--border))",
        strokeWidth: highlighted ? 2 : 1,
        opacity: dimmed ? 0.15 : 1,
        transition: "opacity 0.2s, stroke 0.2s",
      },
      markerEnd: {
        type: MarkerType.ArrowClosed,
        width: 16,
        height: 16,
        color: highlighted ? "hsl(var(--primary))" : "hsl(var(--border))",
      },
    };
  });
}
