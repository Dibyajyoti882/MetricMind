"use client";

import { useState } from "react";
import { askMetricMind } from "@/lib/api";
import ChatMessage, { Message } from "@/components/ChatMessage";
import DynamicChart from "@/components/DynamicChart";

const SUGGESTED = [
  "Why did our European margins drop last quarter?",
  "What was total revenue by region in Q3?",
  "Show me margin percent by quarter for Europe",
];

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  async function send(question: string) {
    if (!question.trim() || loading) return;
    setMessages((m) => [...m, { role: "user", content: question }]);
    setInput("");
    setLoading(true);
    try {
      const res = await askMetricMind(question);
      setMessages((m) => [
        ...m,
        { role: "assistant", content: res.answer, transparency: res.transparency },
      ]);
    } catch (err) {
      setMessages((m) => [
        ...m,
        { role: "assistant", content: `Something went wrong: ${(err as Error).message}` },
      ]);
    } finally {
      setLoading(false);
    }
  }

  const lastAssistant = [...messages].reverse().find((m) => m.role === "assistant");

  return (
    <div style={{ maxWidth: 720, margin: "0 auto", padding: 24, minHeight: "100vh", display: "flex", flexDirection: "column" }}>
      <h1 style={{ fontSize: 22 }}>MetricMind</h1>
      <p style={{ color: "#666", marginTop: -8 }}>Governed conversational BI — every number traces back to the semantic layer.</p>

      {messages.length === 0 && (
        <div style={{ display: "flex", flexWrap: "wrap", gap: 8, margin: "16px 0" }}>
          {SUGGESTED.map((q) => (
            <button
              key={q}
              onClick={() => send(q)}
              style={{ fontSize: 13, padding: "8px 12px", borderRadius: 20, border: "1px solid #ddd", background: "#fff", cursor: "pointer" }}
            >
              {q}
            </button>
          ))}
        </div>
      )}

      <div style={{ flex: 1, marginTop: 12 }}>
        {messages.map((m, i) => (
          <ChatMessage key={i} message={m} />
        ))}
        {loading && <div style={{ color: "#999", fontSize: 14 }}>MetricMind is querying the semantic layer…</div>}
        {lastAssistant?.transparency && <DynamicChart steps={lastAssistant.transparency} />}
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          send(input);
        }}
        style={{ display: "flex", gap: 8, marginTop: 16 }}
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a business question…"
          style={{ flex: 1, padding: "10px 14px", borderRadius: 8, border: "1px solid #ddd" }}
        />
        <button type="submit" disabled={loading} style={{ padding: "10px 18px", borderRadius: 8, background: "#4f46e5", color: "#fff", border: "none" }}>
          Ask
        </button>
      </form>
    </div>
  );
}