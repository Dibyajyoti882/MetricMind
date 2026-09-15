# Git Workflow

**Rule: nobody pushes directly to `main`.** Every member works on their own
branch, opens a PR, and the Team Lead (Member 1) reviews and merges.

## One-time setup (Team Lead)

```bash
cd MetricMind
git init
git add .
git commit -m "Initial project scaffold"
git branch -M main
git remote add origin <YOUR_REPO_URL>
git push -u origin main

git switch -c member1-lead && git push -u origin member1-lead
git switch main
git switch -c member2-data && git push -u origin member2-data
git switch main
git switch -c member3-semantic && git push -u origin member3-semantic
git switch main
git switch -c member4-ai && git push -u origin member4-ai
git switch main
git switch -c member5-frontend && git push -u origin member5-frontend
git switch main
```

## Every day, every member

**1. Start work — sync your branch with the latest main:**
```bash
git switch main
git pull origin main
git switch YOUR-BRANCH
git merge main
```

**2. Do your work, then commit:**
```bash
git status
git add .
git commit -m "Describe what you did"
git push origin YOUR-BRANCH
```

**3. Open a Pull Request on GitHub:** base `main` ← compare `YOUR-BRANCH`.
Team Lead reviews and merges.

## Avoiding merge conflicts

File ownership is split by folder so branches rarely touch the same file:

| Branch | Owns |
|---|---|
| member1-lead | `backend/app/main.py`, `backend/app/routes/`, `docs/` |
| member2-data | `data/`, `dbt/models/staging/`, `dbt/seeds/` |
| member3-semantic | `semantic/`, `dbt/models/marts/` |
| member4-ai | `backend/app/agent/` |
| member5-frontend | `frontend/` |

If two people must touch the same file (e.g. `backend/requirements.txt`),
say so in Slack/Discord before editing it.