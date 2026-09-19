"use client";

import ReactECharts from "echarts-for-react";
import type { TransparencyStep } from "@/lib/api";

function pickChartableStep(
  steps: TransparencyStep[]
): TransparencyStep | null {
  for (let i = steps.length - 1; i >= 0; i--) {
    if (steps[i].data && steps[i].data!.length > 1) {
      return steps[i];
    }
  }

  return null;
}

export default function DynamicChart({
  steps,
}: {
  steps: TransparencyStep[];
}) {
  const step = pickChartableStep(steps);

  if (!step?.data || step.data.length < 2) {
    return null;
  }

  const rows = step.data;

  const keys = Object.keys(rows[0]);

  if (keys.length < 2) {
    return null;
  }

  const measureKey =
    keys.find((key) => key.includes(".")) ??
    keys[keys.length - 1];

  const dimensionKey =
    keys.find((key) => key !== measureKey) ?? keys[0];

  const categories = rows.map((row) =>
    String(row[dimensionKey])
  );

  const values = rows.map((row) => {
    const value = Number(row[measureKey]);
    return Number.isFinite(value) ? value : 0;
  });

  const isTimeSeries =
    dimensionKey.toLowerCase().includes("date") ||
    dimensionKey.toLowerCase().includes("time") ||
    dimensionKey.toLowerCase().includes("quarter") ||
    dimensionKey.toLowerCase().includes("month");

  const option = {
    animationDuration: 700,

    tooltip: {
      trigger: "axis",
    },

    grid: {
      left: 45,
      right: 25,
      top: 25,
      bottom: 35,
      containLabel: true,
    },

    xAxis: {
      type: "category",
      data: categories,
      axisLine: {
        lineStyle: {
          color: "#dfe3eb",
        },
      },
      axisLabel: {
        color: "#788296",
        fontSize: 11,
      },
    },

    yAxis: {
      type: "value",
      splitLine: {
        lineStyle: {
          color: "#eef0f4",
        },
      },
      axisLabel: {
        color: "#788296",
        fontSize: 11,
      },
    },

    series: [
      {
        data: values,
        type: isTimeSeries ? "line" : "bar",
        smooth: isTimeSeries,

        barMaxWidth: 42,

        lineStyle: {
          width: 3,
        },

        itemStyle: {
          color: "#4f46e5",
          borderRadius: isTimeSeries ? 0 : [6, 6, 0, 0],
        },

        areaStyle: isTimeSeries
          ? {
              opacity: 0.08,
            }
          : undefined,

        emphasis: {
          focus: "series",
        },
      },
    ],
  };

  return (
    <div className="chart-card">
      <div className="chart-header">
        <div>
          <div className="chart-title">
            Data visualization
          </div>

          <div className="chart-subtitle">
            {dimensionKey} vs {measureKey}
          </div>
        </div>
      </div>

      <ReactECharts
        option={option}
        style={{
          height: 300,
          width: "100%",
        }}
      />
    </div>
  );
}