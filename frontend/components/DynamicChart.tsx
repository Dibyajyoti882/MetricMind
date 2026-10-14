"use client";

import ReactECharts from "echarts-for-react";
import type { TransparencyStep } from "@/lib/api";

function pickChartableStep(
  steps: TransparencyStep[]
): TransparencyStep | null {
  for (let i = steps.length - 1; i >= 0; i--) {
    const step = steps[i];

    if (step?.data && step.data.length > 1) {
      return step;
    }
  }

  return null;
}

function cleanLabel(key: string): string {
  return key
    .replace(/^.*\./, "")
    .replace(/([A-Z])/g, " $1")
    .replace(/_/g, " ")
    .replace(/\b\w/g, (char) => char.toUpperCase())
    .trim();
}

function isNumericValue(value: unknown): boolean {
  if (typeof value === "number") {
    return Number.isFinite(value);
  }

  if (typeof value === "string" && value.trim() !== "") {
    const parsed = Number(value);
    return Number.isFinite(parsed);
  }

  return false;
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

  /*
   * Find columns containing numeric values.
   * These are treated as measures.
   */
  const numericKeys = keys.filter((key) =>
    rows.some((row) => isNumericValue(row[key]))
  );

  if (numericKeys.length === 0) {
    return null;
  }

  /*
   * Use the last numeric column as the primary measure.
   * This works well with Cube responses where dimensions
   * are strings and measures are numeric.
   */
  const measureKey = numericKeys[numericKeys.length - 1];

  /*
   * Choose the first non-numeric column as the dimension.
   */
  const dimensionKey =
    keys.find((key) => !numericKeys.includes(key)) ?? keys[0];

  const categories = rows.map((row) =>
    String(row[dimensionKey] ?? "")
  );

  const values = rows.map((row) => {
    const value = Number(row[measureKey]);
    return Number.isFinite(value) ? value : 0;
  });

  const dimensionLabel = cleanLabel(dimensionKey);
  const measureLabel = cleanLabel(measureKey);

  const lowerDimension = dimensionKey.toLowerCase();

  const isTimeSeries =
    lowerDimension.includes("date") ||
    lowerDimension.includes("time") ||
    lowerDimension.includes("quarter") ||
    lowerDimension.includes("month") ||
    lowerDimension.includes("year");

  const option = {
    animationDuration: 700,

    tooltip: {
      trigger: "axis",
      axisPointer: {
        type: "shadow",
      },
      formatter: (params: Array<{ axisValue: string; value: number }>) => {
        const item = params[0];

        if (!item) {
          return "";
        }

        return `
          <div style="font-weight:600;margin-bottom:4px;">
            ${item.axisValue}
          </div>
          <div>
            ${measureLabel}: <strong>${item.value}</strong>
          </div>
        `;
      },
    },

    grid: {
      left: 55,
      right: 25,
      top: 30,
      bottom: 45,
      containLabel: true,
    },

    xAxis: {
      type: "category",
      data: categories,
      boundaryGap: !isTimeSeries,

      axisLine: {
        lineStyle: {
          color: "#dfe3eb",
        },
      },

      axisTick: {
        show: false,
      },

      axisLabel: {
        color: "#788296",
        fontSize: 11,
        interval: 0,
        rotate: categories.length > 7 ? 30 : 0,
      },
    },

    yAxis: {
      type: "value",

      axisLine: {
        show: false,
      },

      axisTick: {
        show: false,
      },

      axisLabel: {
        color: "#788296",
        fontSize: 11,
      },

      splitLine: {
        lineStyle: {
          color: "#eef0f4",
        },
      },
    },

    series: [
      {
        name: measureLabel,
        data: values,
        type: isTimeSeries ? "line" : "bar",
        smooth: isTimeSeries,

        barMaxWidth: 42,

        lineStyle: {
          width: 3,
        },

        itemStyle: {
          color: "#4f46e5",
          borderRadius: isTimeSeries
            ? 0
            : [6, 6, 0, 0],
        },

        areaStyle: isTimeSeries
          ? {
              opacity: 0.08,
            }
          : undefined,

        symbolSize: isTimeSeries ? 7 : undefined,

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
            {dimensionLabel} vs {measureLabel}
          </div>
        </div>
      </div>

      <ReactECharts
        option={option}
        style={{
          height: 320,
          width: "100%",
        }}
      />
    </div>
  );
}