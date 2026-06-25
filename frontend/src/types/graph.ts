/** Domain types shared across the frontend. Mirrors the backend schemas. */

export interface NodeMetrics {
  lines_of_code: number;
  num_imports: number;
  num_classes: number;
  num_functions: number;
  cyclomatic_complexity: number;
}

export interface GraphNode {
  id: string;
  label: string;
  path: string;
  language: string;
  metrics: NodeMetrics;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  raw_import: string;
}

export interface GraphResponse {
  repository_id: number;
  nodes: GraphNode[];
  edges: GraphEdge[];
}
