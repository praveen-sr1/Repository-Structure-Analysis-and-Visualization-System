/** Repository, stats, and AI summary types. Mirrors the backend schemas. */

export interface RepositorySummary {
  id: number;
  name: string;
  path: string;
  total_files: number;
  total_lines: number;
  total_dependencies: number;
  created_at: string | null;
  last_scanned_at: string | null;
}

export interface ScanRequest {
  path: string;
  name?: string;
}

export interface ScanResponse {
  repository: RepositorySummary;
  nodes_created: number;
  edges_created: number;
  message: string;
}

export interface LanguageBreakdown {
  language: string;
  files: number;
  lines: number;
}

export interface RepositoryStats {
  repository_id: number;
  total_files: number;
  total_lines: number;
  total_dependencies: number;
  total_classes: number;
  total_functions: number;
  average_complexity: number;
  languages: LanguageBreakdown[];
}

export interface FileMetrics {
  path: string;
  name: string;
  language: string;
  lines_of_code: number;
  num_imports: number;
  num_classes: number;
  num_functions: number;
  cyclomatic_complexity: number;
  class_names: string[];
  function_names: string[];
}

export interface SummaryResponse {
  file_path: string;
  content_hash: string;
  summary: string;
  provider: string;
  model: string;
  cached: boolean;
  available: boolean;
}
