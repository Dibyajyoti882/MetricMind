"""
Owner: Member 1 (Lead) / Member 3 contract

The ONLY code path allowed to reach the semantic layer.
Guardrails enforced here: allow-listed names/operators, row cap, query-size cap,
retry on Cube's "Continue wait", clear errors (never invented data).
"""
import json
import os
import re
import time

import httpx

CUBEJS_API_URL = os.getenv("CUBEJS_API_URL", "http://localhost:4000/cubejs-api/v1")
CUBEJS_TOKEN = os.getenv("CUBEJS_TOKEN", "")

MAX_QUERY_LIMIT = 5000
MAX_QUERY_CHARS = 2000
HTTP_TIMEOUT = 20.0
CONTINUE_WAIT_RETRIES = 5

ALLOWED_MEASURES = {
    "Sales.count", "Sales.revenue", "Sales.materialCost", "Sales.shippingCost",
    "Sales.totalCost", "Sales.margin", "Sales.marginPct",
}
ALLOWED_DIMENSIONS = {
    "Sales.orderId", "Sales.orderDate", "Sales.quarter", "Sales.region",
    "Sales.country", "Sales.productName", "Sales.category",
}
ALLOWED_OPERATORS = {
    "equals", "notEquals", "contains", "notContains", "startsWith", "notStartsWith",
    "endsWith", "notEndsWith", "gt", "gte", "lt", "lte", "set", "notSet",
}

# LLMs occasionally emit invisible characters (e.g. "equals" + U+200D), which Cube rejects.
_INVISIBLE = re.compile("[\u200b\u200c\u200d\u2060\ufeff\u00ad]")


class SemanticLayerError(Exception):
    pass


def _clean(obj):
    if isinstance(obj, str):
        return _INVISIBLE.sub("", obj).strip()
    if isinstance(obj, list):
        return [_clean(x) for x in obj]
    if isinstance(obj, dict):
        return {_clean(k): _clean(v) for k, v in obj.items()}
    return obj


def _validate(measures, dimensions, filters, time_dimensions):
    if not measures:
        raise SemanticLayerError("At least one measure is required.")
    bad = [m for m in measures if m not in ALLOWED_MEASURES]
    if bad:
        raise SemanticLayerError(f"Unknown measure(s) {bad}. Allowed: {sorted(ALLOWED_MEASURES)}")
    bad = [d for d in dimensions if d not in ALLOWED_DIMENSIONS]
    if bad:
        raise SemanticLayerError(f"Unknown dimension(s) {bad}. Allowed: {sorted(ALLOWED_DIMENSIONS)}")
    for f in filters:
        if not isinstance(f, dict) or f.get("member") not in ALLOWED_DIMENSIONS | ALLOWED_MEASURES:
            raise SemanticLayerError(f"Invalid filter member in {f!r}")
        if f.get("operator") not in ALLOWED_OPERATORS:
            raise SemanticLayerError(
                f"Invalid filter operator {f.get('operator')!r}. Allowed: {sorted(ALLOWED_OPERATORS)}")
        if "values" in f and not isinstance(f["values"], list):
            raise SemanticLayerError("Filter 'values' must be a list.")
    for t in time_dimensions:
        if not isinstance(t, dict) or t.get("dimension") not in ALLOWED_DIMENSIONS:
            raise SemanticLayerError(f"Invalid time dimension in {t!r}")


def run_query(measures, dimensions=None, filters=None, time_dimensions=None, limit=1000):
    """Run a governed query. Returns {"query", "generated_sql", "data"}."""
    dimensions = list(dimensions or [])
    filters = list(filters or [])
    time_dimensions = list(time_dimensions or [])
    measures = list(measures or [])

    measures, dimensions = _clean(measures), _clean(dimensions)
    filters, time_dimensions = _clean(filters), _clean(time_dimensions)

    _validate(measures, dimensions, filters, time_dimensions)

    query = {
        "measures": measures,
        "dimensions": dimensions,
        "filters": filters,
        "timeDimensions": time_dimensions,
        "limit": max(1, min(int(limit), MAX_QUERY_LIMIT)),
    }
    payload = json.dumps(query)
    if len(payload) > MAX_QUERY_CHARS:
        raise SemanticLayerError("Query too large; simplify it.")

    headers = {"Content-Type": "application/json"}
    if CUBEJS_TOKEN:
        headers["Authorization"] = CUBEJS_TOKEN

    last_err = None
    for attempt in range(CONTINUE_WAIT_RETRIES):
        try:
            resp = httpx.get(f"{CUBEJS_API_URL}/load", params={"query": payload},
                             headers=headers, timeout=HTTP_TIMEOUT)
        except httpx.TimeoutException as e:
            raise SemanticLayerError("Cube.dev timed out. Is it running on port 4000?") from e
        except httpx.HTTPError as e:
            raise SemanticLayerError(f"Cannot reach Cube.dev: {e}") from e

        if resp.status_code == 403:
            raise SemanticLayerError(
                "Cube.dev rejected the token (403). Check CUBEJS_TOKEN in backend/.env "
                "matches CUBEJS_API_SECRET in semantic/.env.")
        try:
            body = resp.json()
        except ValueError:
            body = {}

        if resp.status_code == 200 and body.get("error") == "Continue wait":
            time.sleep(0.5 * (attempt + 1))
            last_err = "Cube.dev still computing"
            continue
        if resp.status_code >= 400 or body.get("error"):
            raise SemanticLayerError(
                f"Cube.dev error {resp.status_code}: {body.get('error') or resp.text[:300]}")

        return {
            "query": query,
            "generated_sql": body.get("sqlQuery") or None,
            "data": body.get("data", []),
        }
    raise SemanticLayerError(last_err or "Cube.dev did not return a result.")