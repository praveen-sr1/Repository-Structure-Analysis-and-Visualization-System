import { describe, expect, it } from "vitest";

import type { GraphEdge, GraphNode } from "@/types";
import { toFlowEdges, toFlowNodes } from "@/utils/graphTransform";

function node(id: string): GraphNode {
  return {
    id,
    label: id,
    path: id,
    language: "python",
    metrics: {
      lines_of_code: 10,
      num_imports: 1,
      num_classes: 0,
      num_functions: 1,
      cyclomatic_complexity: 2,
    },
  };
}

describe("graphTransform", () => {
  const nodes: GraphNode[] = [node("a.py"), node("b.py"), node("c.py")];
  const edges: GraphEdge[] = [
    { id: "e1", source: "a.py", target: "b.py", raw_import: "b" },
    { id: "e2", source: "b.py", target: "c.py", raw_import: "c" },
  ];

  it("creates one flow node per graph node with positions", () => {
    const flowNodes = toFlowNodes(nodes, edges);
    expect(flowNodes).toHaveLength(3);
    for (const n of flowNodes) {
      expect(n.type).toBe("fileNode");
      expect(typeof n.position.x).toBe("number");
      expect(typeof n.position.y).toBe("number");
    }
  });

  it("ranks nodes by dependency depth (a < b < c on the x-axis)", () => {
    const flowNodes = toFlowNodes(nodes, edges);
    const byId = Object.fromEntries(flowNodes.map((n) => [n.id, n]));
    expect(byId["a.py"].position.x).toBeLessThan(byId["b.py"].position.x);
    expect(byId["b.py"].position.x).toBeLessThan(byId["c.py"].position.x);
  });

  it("marks highlighted edges as animated and dims the rest", () => {
    const highlighted = new Set(["e1"]);
    const flowEdges = toFlowEdges(edges, highlighted, true);
    const e1 = flowEdges.find((e) => e.id === "e1")!;
    const e2 = flowEdges.find((e) => e.id === "e2")!;
    expect(e1.animated).toBe(true);
    expect(e2.animated).toBe(false);
    expect(e2.style?.opacity).toBeLessThan(1);
  });

  it("tolerates cycles without infinite recursion", () => {
    const cyclic: GraphEdge[] = [
      { id: "e1", source: "a.py", target: "b.py", raw_import: "b" },
      { id: "e2", source: "b.py", target: "a.py", raw_import: "a" },
    ];
    expect(() => toFlowNodes([node("a.py"), node("b.py")], cyclic)).not.toThrow();
  });
});
