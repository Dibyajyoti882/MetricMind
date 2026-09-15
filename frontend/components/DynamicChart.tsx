"use client";

import ReactECharts from "echarts-for-react";
import type { TransparencyStep } from "@/lib/api";

function pickChartableStep(steps: TransparencyStep[]): TransparencyStep | null {
  for (let i = steps.length - 1; i >= 0; i--) {
    if (steps[i].data && steps[i].data!.length > 1) return steps[i];
  }
  return null;
}

export default function DynamicChart({ steps }: { steps: TransparencyStep[] }) {
  const step = pickChartableStep(steps);
  if (!step || !step.data) return null;

  const rows = step.data;
  const keys = Object.keys(rows[0]);
  const measureKey = keys.find((k) => k.includes(".")) ?? keys[keys.length - 1];
  const dimensionKey = keys.find((k) => k !== measureKey) ?? keys[0];

  const isTimeSeries = dimensionKey.toLowerCase().includes("date") || dimensionKey.toLowerCase().includes("time");

  const categories = rows.map((r) => String(r[dimensionKey]));
  const values = rows.map((r) => Number(r[measureKey]));

  const option = {
    xAxis: { type: "category", data: categories },
    yAxis: { type: "value" },
    series: [
      {
        data: values,
        type: isTimeSeries ? "line" : "bar",
        smooth: isTimeSeries,
        itemStyle: { color: "#4f46e5" },
      },
    ],
    tooltip: { trigger: "axis" },
    grid: { left: 40, right: 20, top: 20, bottom: 30 },
  };

  return (
    <div style={{ marginTop: 12, background: "#fff", borderRadius: 12, padding: 8 }}>
      <ReactECharts option={option} style={{ height: 260 }} />
    </div>
  );
}