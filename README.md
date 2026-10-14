# MetricMind — Agentic Semantic BI Engine

A governed conversational BI system. Ask a business question in plain English and get an
answer built from **governed metric definitions**, not from SQL the AI made up.

> Demo question: **"Why did our European margins drop last quarter?"**

## The problem

When an LLM gets raw access to a data warehouse ("Text-to-SQL"), it can hallucinate joins,
ignore business rules, and report revenue that doesn't match official figures. People stop
trusting the numbers.

## The idea

Business metrics (Revenue, Cost, Margin, Margin %) are defined **once, as code**, in a semantic
layer. The AI can only ask the semantic layer for those named metrics. It has no tool for
writing SQL. Finance and Sales always see the same number, and every answer shows the exact
query behind it.

## Architecture

```
Next.js chat UI  (frontend/)
        │  POST /api/query
        ▼
FastAPI backend  (backend/)  ── routing: simple / "why" / complex
        │                │
        │                └── direct path (no LLM)  ──┐
        ▼                                            │
LangChain agent  (backend/app/agent/)                │
   one tool only: query_semantic_layer               │
        │                                            │
        ▼                                            ▼
Semantic client  (backend/app/semantic_client/)  ◄───┘
   allow-listed measures, row cap, error handling
        │  REST + JWT
        ▼
Cube.dev semantic layer  (semantic/)
        │  governed SQL
        ▼
DuckDB warehouse  ◄──  dbt models (dbt/)  ◄──  mock data (data/)
```

## Tech stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14, React, ECharts |
| Backend | FastAPI, Pydantic, httpx |
| Agent | LangChain 0.3 (tool calling) with Gemini, Claude or Grok |
| Semantic layer | Cube.dev |
| Transformations | dbt (dbt-duckdb) |
| Warehouse | DuckDB locally. Snowflake is a config change |
| Data | Python-generated mock sales data |

## Repository layout

```
MetricMind/
├── data/               mock data generator
├── dbt/                seeds -> staging views -> fct_sales mart (+ tests)
├── semantic/           Cube.dev config and the Sales cube
├── backend/
│   └── app/
│       ├── main.py             FastAPI app
│       ├── routes/query.py     routing between direct path and agent
│       ├── analytics.py        direct (no-LLM) analytics and root-cause analysis
│       ├── agent/              LangChain agent, tool, prompts
│       └── semantic_client/    the only code path to Cube.dev
├── frontend/           chat UI, dynamic charts, query-trail panel
├── tests/              unit tests
└── docs/               Git workflow and sprint plans
```

## Prerequisites

- **Python 3.11** (not 3.12+). Newer versions break parts of the dependency stack.
- **Node.js 18+** and npm
- **Git**
- An LLM API key is optional. See [Routing modes](#routing-modes).

## Setup

All commands below are PowerShell on Windows. Run them from the repo root unless noted.

### 1. Generate the data

```powershell
cd data
python generate_mock_data.py
cd ..
```

### 2. Build the warehouse with dbt

```powershell
cd dbt
pip install dbt-duckdb

copy ..\data\sales.csv seeds\raw_sales.csv
copy ..\data\costs.csv seeds\raw_costs.csv
copy ..\data\customers.csv seeds\raw_customers.csv
copy ..\data\products.csv seeds\raw_products.csv
copy ..\data\geography.csv seeds\raw_geography.csv

$env:DBT_PROFILES_DIR="."
dbt seed
dbt run
dbt test
cd ..
```

This creates `warehouse.duckdb` in the repo root. All 5 tests should pass.
(On Mac/Linux you can use `bash dbt/load_seeds.sh` instead of the copy commands.)

### 3. Configure the semantic layer

Create `semantic/.env`:

```
CUBEJS_API_SECRET=metricmind-dev-secret-2026
CUBEJS_DEV_MODE=true
CUBEJS_DB_TYPE=duckdb
CUBEJS_DB_DUCKDB_DATABASE_PATH=C:\full\path\to\MetricMind\warehouse.duckdb
```

Use the **absolute** path to `warehouse.duckdb`. Then:

```powershell
cd semantic
npm install
```

Generate a token signed with the same secret:

```powershell
node -e "console.log(require('jsonwebtoken').sign({}, 'metricmind-dev-secret-2026'))"
```

Copy the printed token for the next step.

### 4. Configure the backend

```powershell
cd backend
py -3.11 -m venv venv
venv\Scripts\activate
python --version          # must say 3.11.x
pip install -r requirements.txt
copy .env.example .env
notepad .env
```

Fill in `backend/.env`:

```
# LLM: set ONE key. Provider is auto-detected, or force it with LLM_PROVIDER
GOOGLE_API_KEY=
ANTHROPIC_API_KEY=
XAI_API_KEY=
# LLM_PROVIDER=gemini        # gemini | anthropic | xai
# AGENT_MODEL=               # optional; unset uses the provider default

ROUTING_MODE=auto            # auto | direct | agent

CUBEJS_API_URL=http://localhost:4000/cubejs-api/v1
CUBEJS_TOKEN=<the token from step 3>
```

`.env` files are gitignored. Never commit keys.

### 5. Install the frontend

```powershell
cd frontend
npm install
```

## Run

Open three terminals, in this order:

| # | Service | Commands | Port |
|---|---|---|---|
| 1 | Cube.dev | `cd semantic` then `npm run dev` | 4000 |
| 2 | Backend | `cd backend`, `venv\Scripts\activate`, then `uvicorn app.main:app --reload --port 8000` | 8000 |
| 3 | Frontend | `cd frontend` then `npm run dev` | 3000 |

Open **http://localhost:3000** and ask a question. Check the backend at
http://localhost:8000/api/health, which should return `{"status":"ok"}`. The Cube Playground at
http://localhost:4000 lets you run governed queries by hand.

Every new terminal needs the venv activated before running backend commands.

## Routing modes

Set `ROUTING_MODE` in `backend/.env`.

| Question type | `auto` (default) | `direct` | `agent` |
|---|---|---|---|
| Simple ("revenue by region in Q3") | Direct Cube.dev query, no LLM | Same | LLM agent |
| "Why did X drop?" | LLM agent, falls back to direct analysis if the LLM is unavailable | Direct analysis, no LLM | LLM agent |
| Complex / open-ended | LLM agent, or a clear 503 if the LLM is down | Agent | LLM agent |

Use `direct` for the most reliable demo. The answer labels itself when it was computed without an
LLM, and the API response carries `mode: "agent" | "direct" | "fallback"`.

## API

`POST /api/query`

```json
{ "question": "Why did our European margins drop last quarter?" }
```

Response:

```json
{
  "answer": "markdown text with the explanation and a table",
  "transparency": [
    { "tool": "query_semantic_layer", "query": {}, "generated_sql": "...", "data": [], "error": null }
  ],
  "mode": "direct",
  "note": null,
  "chart": { "type": "bar", "x": ["Q1", "Q2", "Q3"], "series": [{ "name": "Margin %", "values": [49.5, 49.6, 34.3] }] },
  "cached": false
}
```

| Status | Meaning |
|---|---|
| 400 | Empty or over-long question (max 500 characters) |
| 502 | Cube.dev problem (down, bad token, bad query) |
| 503 | The question needs the LLM and the LLM is unavailable |

`GET /api/health` returns `{"status": "ok"}`.

## Governance features

- **No SQL tool.** The agent's only data tool is `query_semantic_layer`.
- **Allow-listed names.** Only governed measures and dimensions are accepted. Unknown names are rejected in `cube_client.py`, not just discouraged in the prompt.
- **Metrics defined once.** Margin is computed only in `fct_sales`. `marginPct` is a weighted ratio, never an average of row percentages.
- **Cost controls.** 5,000-row cap (in Cube config and client), query-size cap, at most 5 agent iterations, and a 10-minute cache for repeated questions.
- **Transparency.** Every answer includes the exact semantic queries and compiled SQL ("View query trail").
- **Honest failures.** Errors are returned as messages. The system never fills gaps with invented numbers.
- **Audit.** Run the same query repeatedly in the Cube Playground and the result is identical (see `semantic/GOVERNANCE_TEST.md`).

## The demo data story

The generator deliberately builds a margin drop into Europe's Q3 data:

| Quarter | Europe margin | Shipping cost, % of revenue |
|---|---|---|
| Q1 | ~49.5% | ~10% |
| Q2 | ~49.6% | ~10% |
| Q3 | ~34.3% | ~25% |

Material cost stays flat at about 40%. Shipping cost is the root cause, and the multi-step
analysis finds it by comparing cost components as a share of revenue.
(Exact figures depend on your generated data.)

## Testing

```powershell
cd backend
venv\Scripts\activate
cd ..
python -m pip install pytest
python -m pytest tests -q          # unit tests, no Cube.dev needed
cd dbt
dbt test                            # data tests on fct_sales
```

## Team workflow

Five members, five branches. Nobody pushes work directly to `main`.

| Branch | Owner | Folders |
|---|---|---|
| `member1-lead` | Team Lead | `backend/` (API, routing, client), `docs/`, root files |
| `member2-data` | Data Engineer | `data/`, `dbt/models/staging/`, `dbt/seeds/` |
| `member3-semantic` | Semantic Engineer | `semantic/`, `dbt/models/marts/` |
| `member4-ai` | AI Engineer | `backend/app/agent/` |
| `member5-frontend` | Frontend Engineer | `frontend/` |

```powershell
git switch main
git pull origin main
git switch YOUR-BRANCH
git merge main
# ... work ...
git add .
git commit -m "feat(area): what you did"
git push origin YOUR-BRANCH
# open a Pull Request into main; the Lead reviews and merges
```

See `docs/GIT_WORKFLOW.md`.

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| numpy / meson / "GCC >= 8.4" error on `pip install` | Wrong Python. Use a 3.11 venv: `py -3.11 -m venv venv` |
| `cannot import name 'AgentExecutor'` | LangChain 1.x installed, or venv not active. Use the pinned `requirements.txt` inside the 3.11 venv |
| "Failed to fetch" in the UI | Backend isn't running, or crashed on startup |
| Cube.dev 403 / "Authorization header isn't set" | `CUBEJS_TOKEN` must be signed with the same secret as `CUBEJS_API_SECRET` |
| Cube.dev "Unsupported db type: undefined" | Set `CUBEJS_DB_TYPE=duckdb` in `semantic/.env` |
| `dbt run` says raw table doesn't exist | Run `dbt seed` first, with the CSVs copied into `dbt/seeds/` |
| `bash` not recognised for `load_seeds.sh` | Use the `copy` commands from setup step 2 |
| Push rejected by GitHub secret scanning | A real key is in a committed file. Remove it, and keep keys only in `.env` |
| LLM 404 "model no longer available" | Provider retired the model. Set `AGENT_MODEL` to a current one |
| LLM 429 "quota exceeded" | Free-tier limit reached. Wait, switch key/provider, or use `ROUTING_MODE=direct` |
| LLM 400 "thought_signature" | A Gemini thinking model with this LangChain version. Use another model or provider |
| LLM "credit balance too low" | Provider account has no credit. Add credit or switch provider |

## Known limitations

- Mock data only, and a single `Sales` cube.
- Local DuckDB instead of Snowflake or Databricks.
- The live LLM agent depends on an external provider. Free tiers change model names and limits often, so check the provider's current model list before relying on one.
- Cube.dev runs in dev mode with a shared dev secret. Production needs proper auth.

## Future scope

- More cubes (customers, churn, time dimension)
- Snowflake or Databricks connection
- Role-based access and per-user security contexts
- Streaming responses in the chat UI
- Cube Store caching and pre-aggregations
- Automated governance audit in CI
