const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export interface TransparencyStep {
  tool: string;
  tool_input: Record<string, unknown>;
  query: Record<string, unknown> | null;
  generated_sql: string | null;
  data: Record<string, unknown>[] | null;
}

export interface QueryResponse {
  answer: string;
  transparency: TransparencyStep[];
}

export async function askMetricMind(question: string): Promise<QueryResponse> {
  const res = await fetch(`${API_BASE}/api/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`API error ${res.status}: ${detail}`);
  }
  return res.json();
}