export type QueryResponse = {
  session_id: string;
  answer: string;
  sources: string[];
};

function apiBase(): string {
  return (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000").replace(/\/$/, "");
}

/**
 * POST /api/query — RAG + conversational memory (FastAPI backend).
 */
export async function postQuery(
  query: string,
  sessionId: string | null,
): Promise<QueryResponse> {
  const res = await fetch(`${apiBase()}/api/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      query,
      session_id: sessionId ?? null,
    }),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `Request failed (${res.status})`);
  }

  return res.json() as Promise<QueryResponse>;
}
