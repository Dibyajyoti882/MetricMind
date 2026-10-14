"""
Direct (no-LLM) analytics: answers supported questions straight from the governed
semantic layer. Used for simple questions and as a fallback when the LLM is unavailable.
"""
import re

from app.semantic_client.cube_client import run_query

REGIONS = {
    "europe": "Europe", "european": "Europe",
    "north america": "North America", "usa": "North America",
    "apac": "APAC", "asia": "APAC",
}
QUARTER_ORDER = ["Q1", "Q2", "Q3", "Q4"]

LABELS = {
    "Sales.revenue": "Revenue", "Sales.totalCost": "Total cost", "Sales.margin": "Margin",
    "Sales.marginPct": "Margin %", "Sales.materialCost": "Material cost",
    "Sales.shippingCost": "Shipping cost", "Sales.count": "Orders",
    "Sales.quarter": "Quarter", "Sales.region": "Region", "Sales.country": "Country",
    "Sales.category": "Category", "Sales.productName": "Product",
}
COMPLEX_WORDS = ("recommend", "predict", "forecast", "should we", "what if", "explain",
                 "how can", "how do", "strategy", "improve")


def _region(q):
    for k, v in REGIONS.items():
        if re.search(rf"\b{re.escape(k)}\b", q):
            return v
    return None


def _quarter(q):
    m = re.search(r"\bq([1-4])\b", q)
    return f"Q{m.group(1)}" if m else None


def classify(question: str):
    """Return ('rca', {...}) | ('simple', {...}) | ('complex', {})."""
    q = question.lower()
    region, quarter = _region(q), _quarter(q)

    if re.search(r"\bwhy\b", q) and re.search(r"margin|drop|declin|fell|decreas|lower|down", q):
        return "rca", {"region": region, "quarter": quarter}
    if any(w in q for w in COMPLEX_WORDS) or re.search(r"\bwhy\b", q):
        return "complex", {}

    measures = []
    if re.search(r"margin\s*(%|percent|percentage|pct)", q):
        measures.append("Sales.marginPct")
    elif "margin" in q:
        measures.append("Sales.margin")
    if re.search(r"revenue|sales", q):
        measures.append("Sales.revenue")
    if "shipping" in q:
        measures.append("Sales.shippingCost")
    if "material" in q:
        measures.append("Sales.materialCost")
    if re.search(r"\bcost", q) and not measures:
        measures.append("Sales.totalCost")
    if not measures:
        return "complex", {}

    dims = []
    if re.search(r"(by|per|each)\s+quarter", q):
        dims.append("Sales.quarter")
    if re.search(r"(by|per|each)\s+region", q):
        dims.append("Sales.region")
    if re.search(r"(by|per|each)\s+country", q):
        dims.append("Sales.country")
    if re.search(r"(by|per|each)\s+categor", q):
        dims.append("Sales.category")
    if re.search(r"(by|per|each)\s+product", q):
        dims.append("Sales.productName")
    return "simple", {"measures": measures, "dimensions": dims, "region": region, "quarter": quarter}


def _filters(region=None, quarter=None):
    f = []
    if region:
        f.append({"member": "Sales.region", "operator": "equals", "values": [region]})
    if quarter:
        f.append({"member": "Sales.quarter", "operator": "equals", "values": [quarter]})
    return f


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _fmt(key, v):
    n = _num(v)
    if n is None:
        return str(v)
    if key == "Sales.marginPct":
        return f"{n * 100:.1f}%"
    return f"{n:,.0f}"


def _table(rows, cols):
    head = "| " + " | ".join(LABELS.get(c, c) for c in cols) + " |"
    sep = "|" + "|".join("---" for _ in cols) + "|"
    body = ["| " + " | ".join(_fmt(c, r.get(c)) for c in cols) + " |" for r in rows]
    return "\n".join([head, sep, *body])


def _step(res):
    return {"tool": "query_semantic_layer", "tool_input": res["query"], "query": res["query"],
            "generated_sql": res["generated_sql"], "data": res["data"], "error": None}


def _qkey(r):
    q = r.get("Sales.quarter")
    return QUARTER_ORDER.index(q) if q in QUARTER_ORDER else 99


def run_simple(spec):
    res = run_query(spec["measures"], spec["dimensions"], _filters(spec["region"], spec["quarter"]))
    rows = res["data"]
    if "Sales.quarter" in spec["dimensions"]:
        rows = sorted(rows, key=_qkey)
    scope = " · ".join(x for x in (spec["region"], spec["quarter"]) if x) or "all data"
    if not rows:
        answer = f"The semantic layer returned no rows for: {scope}."
    else:
        cols = [*spec["dimensions"], *spec["measures"]]
        answer = (f"**{', '.join(LABELS[m] for m in spec['measures'])}** ({scope})\n\n"
                  f"{_table(rows, cols)}\n\nSuggested chart: bar")
    dim = spec["dimensions"][0] if spec["dimensions"] else None
    chart = None
    if dim and rows:
        chart = {"type": "bar", "x": [r[dim] for r in rows],
                 "series": [{"name": LABELS[m], "values": [_num(r.get(m)) for r in rows]}
                            for m in spec["measures"]]}
    return {"answer": answer, "transparency": [_step(res)], "mode": "direct", "chart": chart}


def run_rca(spec):
    region = spec.get("region")
    flt = _filters(region)
    trend = run_query(["Sales.revenue", "Sales.totalCost", "Sales.margin", "Sales.marginPct"],
                      ["Sales.quarter"], flt)
    parts = run_query(["Sales.revenue", "Sales.materialCost", "Sales.shippingCost"],
                      ["Sales.quarter"], flt)
    steps = [_step(trend), _step(parts)]
    scope = region or "All regions"

    t_rows = sorted(trend["data"], key=_qkey)
    p_rows = {r["Sales.quarter"]: r for r in parts["data"]}
    if len(t_rows) < 2:
        return {"answer": f"Not enough quarterly history for {scope} to explain a change.",
                "transparency": steps, "mode": "direct", "chart": None}

    target = spec.get("quarter")
    idx = next((i for i, r in enumerate(t_rows) if r["Sales.quarter"] == target), len(t_rows) - 1)
    idx = max(idx, 1)
    prev, last = t_rows[idx - 1], t_rows[idx]
    pq, lq = prev["Sales.quarter"], last["Sales.quarter"]
    m_prev, m_last = _num(prev["Sales.marginPct"]) * 100, _num(last["Sales.marginPct"]) * 100
    delta = m_last - m_prev

    def share(q, key):
        r = p_rows.get(q, {})
        rev = _num(r.get("Sales.revenue")) or 0
        c = _num(r.get(key)) or 0
        return (c / rev * 100) if rev else 0.0

    comp = {"Material cost": "Sales.materialCost", "Shipping cost": "Sales.shippingCost"}
    shifts = {n: (share(pq, k), share(lq, k)) for n, k in comp.items()}
    driver = max(shifts, key=lambda n: shifts[n][1] - shifts[n][0])
    d_prev, d_last = shifts[driver]

    if delta >= -0.5:
        headline = (f"**{scope} margin did not drop** from {pq} to {lq}: "
                    f"{m_prev:.1f}% → {m_last:.1f}% ({delta:+.1f} pts).")
        cause = ""
    else:
        headline = (f"**{scope} margin fell from {m_prev:.1f}% in {pq} to {m_last:.1f}% in {lq}** "
                    f"({delta:+.1f} pts).")
        other = [n for n in shifts if n != driver][0]
        o_prev, o_last = shifts[other]
        cause = (f"\n\n**Main driver: {driver.lower()}.** It rose from {d_prev:.1f}% to {d_last:.1f}% "
                 f"of revenue ({d_last - d_prev:+.1f} pts), while {other.lower()} moved "
                 f"{o_prev:.1f}% → {o_last:.1f}% ({o_last - o_prev:+.1f} pts).")

    qs = [r["Sales.quarter"] for r in t_rows]
    table = ["| Quarter | Revenue | Material % | Shipping % | Margin % |", "|---|---|---|---|---|"]
    for r in t_rows:
        q = r["Sales.quarter"]
        table.append(f"| {q} | {_fmt('Sales.revenue', r['Sales.revenue'])} | "
                     f"{share(q, 'Sales.materialCost'):.1f}% | {share(q, 'Sales.shippingCost'):.1f}% | "
                     f"{_num(r['Sales.marginPct']) * 100:.1f}% |")
    answer = (f"{headline}{cause}\n\n" + "\n".join(table) +
              "\n\nSuggested chart: bar\n\n"
              "_Computed directly from the governed semantic layer (2 queries, no LLM)._")
    chart = {"type": "bar", "x": qs,
             "series": [{"name": "Margin %", "values": [round(_num(r["Sales.marginPct"]) * 100, 1) for r in t_rows]},
                        {"name": "Shipping % of revenue", "values": [round(share(q, "Sales.shippingCost"), 1) for q in qs]},
                        {"name": "Material % of revenue", "values": [round(share(q, "Sales.materialCost"), 1) for q in qs]}]}
    return {"answer": answer, "transparency": steps, "mode": "direct", "chart": chart}