/**
 * Graph interaction store (Zustand).
 *
 * Derives the set of nodes/edges that should be highlighted when a node is
 * selected, so the canvas can dim everything that is not directly connected to
 * the current selection.
 */
import { create } from "zustand";

import type { GraphEdge } from "@/types";

interface GraphInteractionState {
  highlightedNodes: Set<string>;
  highlightedEdges: Set<string>;
  computeHighlights: (selectedId: string | null, edges: GraphEdge[]) => void;
  clear: () => void;
}

export const useGraphStore = create<GraphInteractionState>((set) => ({
  highlightedNodes: new Set(),
  highlightedEdges: new Set(),

  computeHighlights: (selectedId, edges) => {
    if (!selectedId) {
      set({ highlightedNodes: new Set(), highlightedEdges: new Set() });
      return;
    }
    const nodes = new Set<string>([selectedId]);
    const edgeIds = new Set<string>();
    for (const edge of edges) {
      if (edge.source === selectedId || edge.target === selectedId) {
        nodes.add(edge.source);
        nodes.add(edge.target);
        edgeIds.add(edge.id);
      }
    }
    set({ highlightedNodes: nodes, highlightedEdges: edgeIds });
  },

  clear: () => set({ highlightedNodes: new Set(), highlightedEdges: new Set() }),
}));
