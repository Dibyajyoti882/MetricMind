"""
Owner: Member 1 (Team Lead) / Member 3 (Semantic Engineer) contract
This is the ONLY code path allowed to reach the semantic layer.
"""
import os
import httpx

CUBEJS_API_URL = os.getenv("CUBEJS_API_URL", "http://localhost:4000/cubejs-api/v1")
CUBEJS_TOKEN = os.getenv("CUBEJS_TOKEN", "")

MAX_QUERY_LIMIT = 5000


class SemanticLayerError(Exception):
    pass


def run_query(measures: list[str], dimensions: list[str] | None = None,
              filters: list[dict] | None = None,
              time_dimensions: list[dict] | None = None,
              limit: int = 1000) -> dict:
    query = {
        "measures": measures,
        "dimensions": dimensions or [],
        "filters": filters or [],
        "timeDimensions": time_dimensions or [],
        "limit": min(limit, MAX_QUERY_LIMIT),
    }

    headers = {"Content-Type": "application/json"}
    if CUBEJS_TOKEN:
        headers["Authorization"] = CUBEJS_TOKEN

    try:
        resp = httpx.get(
            f"{CUBEJS_API_URL}/load",
            params={"query": _to_json(query)},
            headers=headers,
            timeout=15.0,
        )
        resp.raise_for_status()
    except httpx.HTTPError as e:
        raise SemanticLayerError(f"Semantic layer call failed: {e}") from e

    data = resp.json()
    return {
        "query": query,
        "generated_sql": data.get("sqlQuery") or data.get("annotation"),
        "data": data.get("data", []),
    }


def _to_json(query: dict) -> str:
    import json
    return json.dumps(query)