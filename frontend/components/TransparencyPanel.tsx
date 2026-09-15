"use client";

import { useState } from "react";
import type { TransparencyStep } from "@/lib/api";

export default function TransparencyPanel({ steps }: { steps: TransparencyStep[] }) {
  const [open, setOpen] = useState(false);

  if (!steps?.length) return null;

  return (
    <div style={{ marginTop: 8 }}>
      <button
        onClick={() => setOpen((o) => !o)}
        style={{
          fontSize: 12,
          padding: "4px 10px",
          borderRadius: 6,
          border: "1px solid #ddd",
          background: "#f7f7f8",
          cursor: "pointer",
        }}
      >
        {open ? "Hide" : "View"} SQL / API Call ({steps.length} step{steps.length > 1 ? "s" : ""})
      </button>

      {open && (
        <div style={{ marginTop: 8, display: "flex", flexDirection: "column", gap: 8 }}>
          {steps.map((step, i) => (
            <div
              key={i}
              style={{
                fontSize: 12,
                background: "#0b1021",
                color: "#d6e0ff",
                padding: 10,
                borderRadius: 8,
                overflowX: "auto",
                fontFamily: "monospace",
              }}
            >
              <div style={{ opacity: 0.7 }}>Step {i + 1} — {step.tool}</div>
              <div>Semantic query: {JSON.stringify(step.query ?? step.tool_input, null, 2)}</div>
              {step.generated_sql && (
                <div style={{ marginTop: 6 }}>Compiled SQL: {step.generated_sql}</div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}