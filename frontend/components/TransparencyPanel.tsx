"use client";

import { useState } from "react";
import type { TransparencyStep } from "@/lib/api";

export default function TransparencyPanel({
  steps,
}: {
  steps: TransparencyStep[];
}) {
  const [open, setOpen] = useState(false);

  if (!steps?.length) {
    return null;
  }

  return (
    <div className="transparency">
      <button
        type="button"
        className="transparency-button"
        onClick={() => setOpen((current) => !current)}
      >
        {open ? "Hide" : "View"} SQL / API Call
        {" · "}
        {steps.length} step{steps.length > 1 ? "s" : ""}
      </button>

      {open && (
        <div className="transparency-content">
          {steps.map((step, index) => (
            <div
              className="transparency-step"
              key={`${step.tool}-${index}`}
            >
              <div className="step-title">
                Step {index + 1} — {step.tool}
              </div>

              <div>
                Semantic query:
              </div>

              <div>
                {JSON.stringify(
                  step.query ?? step.tool_input,
                  null,
                  2
                )}
              </div>

              {step.generated_sql && (
                <div className="sql-block">
                  Compiled SQL:
                  <br />
                  {step.generated_sql}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}