export type QueryResponse = {
  session_id: string;
  answer: string;
  sources: string[];
};

export type UploadResponse = {
  message: string;
  file_path: string;
  document_id: string;
};

function apiBase(): string {
  return (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000").replace(/\/$/, "");
}

function errorBodyMessage(text: string): string {
  try {
    const j = JSON.parse(text) as { detail?: unknown; error?: unknown; message?: unknown };
    if (typeof j.detail === "string") return j.detail;
    if (Array.isArray(j.detail)) return JSON.stringify(j.detail);
    if (typeof j.error === "string") return j.error;
    if (typeof j.message === "string" && j.error) return `${j.error} (${j.message})`;
  } catch {
    /* plain text */
  }
  return text || "Request failed";
}

/**
 * POST /api/upload — multipart form field `file` (.pdf / .txt).
 * Do not set Content-Type: the browser sets multipart boundary for FormData.
 */
export async function postUploadFile(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${apiBase()}/api/upload`, {
    method: "POST",
    body: formData,
    // headers: omit Content-Type for FormData
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(errorBodyMessage(text) || `Upload failed (${res.status})`);
  }

  return res.json() as Promise<UploadResponse>;
}

const QUERY_URL = `${apiBase()}/api/query`;

/**
 * POST http://localhost:8000/api/query — RAG + conversational memory (FastAPI backend).
 */
export async function postQuery(
  query: string,
  sessionId: string | null,
): Promise<QueryResponse> {
  const res = await fetch(QUERY_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify({
      query,
      session_id: sessionId ?? null,
    }),
  });

  if (!res.ok) {
    const text = await res.text();
    const msg = errorBodyMessage(text) || `Request failed (${res.status})`;
    console.error("[api/query]", res.status, msg, { url: QUERY_URL });
    throw new Error(msg);
  }

  return res.json() as Promise<QueryResponse>;
}
