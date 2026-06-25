/**
 * Typed API client.
 *
 * A thin fetch wrapper that centralises base-URL handling, JSON parsing, and
 * error normalisation. All backend calls go through {@link request}.
 */
import type {
  FileMetrics,
  GraphResponse,
  RepositoryStats,
  RepositorySummary,
  ScanRequest,
  ScanResponse,
  SummaryResponse,
} from "@/types";

const BASE_URL =
  (import.meta.env.VITE_API_BASE_URL as string | undefined) ??
  "http://localhost:8000/api";

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...init,
    });
  } catch {
    throw new ApiError(
      "Cannot reach the backend. Is the API server running?",
      0,
    );
  }

  if (!response.ok) {
    let detail = `Request failed with status ${response.status}`;
    try {
      const body = await response.json();
      if (body?.detail) detail = body.detail;
    } catch {
      /* response had no JSON body */
    }
    throw new ApiError(detail, response.status);
  }

  if (response.status === 204) {
    return undefined as T;
  }
  return (await response.json()) as T;
}

export const api = {
  // ---- Repositories ----
  listRepositories: () => request<RepositorySummary[]>("/repositories"),

  getRepository: (id: number) =>
    request<RepositorySummary>(`/repositories/${id}`),

  scanRepository: (payload: ScanRequest) =>
    request<ScanResponse>("/repositories/scan", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  rescanRepository: (id: number) =>
    request<ScanResponse>(`/repositories/${id}/rescan`, { method: "POST" }),

  deleteRepository: (id: number) =>
    request<void>(`/repositories/${id}`, { method: "DELETE" }),

  // ---- Graph & stats ----
  getGraph: (id: number) => request<GraphResponse>(`/repositories/${id}/graph`),

  getStats: (id: number) =>
    request<RepositoryStats>(`/repositories/${id}/stats`),

  // ---- File metrics & AI summary ----
  getFileMetrics: (id: number, path: string) =>
    request<FileMetrics>(
      `/repositories/${id}/files/metrics?path=${encodeURIComponent(path)}`,
    ),

  getFileSummary: (id: number, path: string) =>
    request<SummaryResponse>(
      `/repositories/${id}/files/summary?path=${encodeURIComponent(path)}`,
    ),
};
