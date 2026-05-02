const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// ─── Types ────────────────────────────────────────────────────────────────────

export interface Document {
  id: string;
  filename: string;
  file_type: string;
  file_size: number | null;
  total_chunks: number;
  created_at: string;
  updated_at: string;
}

export interface DocumentList {
  documents: Document[];
  total: number;
}

export interface IngestResponse {
  document_id: string;
  filename: string;
  total_chunks: number;
}

export interface SourceChunk {
  document_id: string;
  filename: string;
  page_number: number | null;
  snippet: string;
  score: number;
}

export interface QueryResponse {
  answer: string;
  sources: SourceChunk[];
  model: string;
  usage: Record<string, number>;
}

export interface HealthResponse {
  status: string;
  db_connected: boolean;
  document_count: number;
  chunk_count: number;
  timestamp: string;
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let message = `HTTP ${res.status}`;
    try {
      const body = await res.json();
      message = body.detail || body.message || message;
    } catch {
      // ignore parse errors
    }
    throw new Error(message);
  }
  return res.json() as Promise<T>;
}

// ─── API Functions ────────────────────────────────────────────────────────────

/**
 * Upload a document file for ingestion.
 */
export async function ingestDocument(file: File): Promise<IngestResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_URL}/api/ingest`, {
    method: "POST",
    body: formData,
  });

  return handleResponse<IngestResponse>(res);
}

/**
 * Send a question and get a RAG-powered answer with sources.
 */
export async function queryDocuments(
  question: string,
  topK = 5
): Promise<QueryResponse> {
  const res = await fetch(`${API_URL}/api/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, top_k: topK }),
  });

  return handleResponse<QueryResponse>(res);
}

/**
 * Fetch the list of all ingested documents.
 */
export async function listDocuments(): Promise<DocumentList> {
  const res = await fetch(`${API_URL}/api/documents`, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  });

  return handleResponse<DocumentList>(res);
}

/**
 * Delete a document by ID (also deletes all its chunks).
 */
export async function deleteDocument(documentId: string): Promise<void> {
  const res = await fetch(`${API_URL}/api/documents/${documentId}`, {
    method: "DELETE",
  });

  if (res.status === 204) return;
  return handleResponse<void>(res);
}

/**
 * Check the health of the API and its dependencies.
 */
export async function getHealth(): Promise<HealthResponse> {
  const res = await fetch(`${API_URL}/api/health`, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
    cache: "no-store",
  });

  return handleResponse<HealthResponse>(res);
}
