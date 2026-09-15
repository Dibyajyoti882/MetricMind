# Day-by-Day Commit Plan (10 different days, real work each day)

Axlero SOP requires commits on **10 different calendar days within the 14
days before Mid Review** — not 10 commits on one day. Each day below maps
to real, runnable work already scaffolded in this repo.

| Day | Member 1 (Lead) | Member 2 (Data) | Member 3 (Semantic) | Member 4 (AI) | Member 5 (Frontend) |
|---|---|---|---|---|---|
| 1 | Push this scaffold, README, branch protection on `main` | Run & tweak `generate_mock_data.py`, commit `data/` script | Commit `semantic/cube.js`, `package.json` | Commit `backend/app/agent/tools.py` schema stub | Commit `frontend/app/page.tsx` skeleton UI |
| 2 | `.env.example`, CORS config in `main.py` | Commit `dbt_project.yml`, `profiles.yml` | Start `Sales.js` — revenue measure only | Draft `prompts.py` system prompt | `components/ChatMessage.tsx` |
| 3 | Wire `routes/query.py` | Commit `stg_sales.sql`, `stg_customers.sql` | Add cost + margin measures to `Sales.js` | Wire `SEMANTIC_SCHEMA_SUMMARY` into prompt | `lib/api.ts` fetch wrapper |
| 4 | Test `/api/health`, `/api/query` locally | Commit `stg_products.sql`, `stg_costs.sql` | Add `quarter`, `region` dimensions | Build `query_semantic_layer` tool | Connect `page.tsx` to real API |
| 5 | Run `dbt run` end-to-end, fix breakages | Commit `fct_sales.sql` | Verify Cube playground returns correct Europe Q3 numbers | Test agent answers a single-metric question | Handle loading/error states |
| 6 | Add `schema.yml` dbt tests, run `dbt test` | Add more mock data variety (edge cases) | Add `marginPct` weighted measure | Add multi-step reasoning instruction to prompt | Add suggested-questions chips |
| 7 | End-to-end smoke test: UI → API → agent → Cube → DuckDB | Validate Q3/Europe numbers by hand | Governance test: same query = same result, 5x | Confirm agent chains 2 tool calls for "why" questions | `DynamicChart.tsx` — bar chart |
| 8 | Cost breakdown integration check | Add shipping/material cost breakdown queries | Expand schema docs / descriptions | Multi-step: margin → cost breakdown by component | `DynamicChart.tsx` — line chart (time series) |
| 9 | Add query limit (cost governance) enforcement test | Full data validation pass (duplicates, nulls) | Run full governance audit script | Add `MAX_QUERY_LIMIT` enforcement + error handling | `TransparencyPanel.tsx` — View SQL/API button |
| 10 | Final Week-2 checkpoint: merge all PRs, tag `v0.1` | Docs: data dictionary in `docs/` | Docs: measure/dimension reference | Docs: prompt design notes | Polish UI, responsive layout pass |

## Commit message convention