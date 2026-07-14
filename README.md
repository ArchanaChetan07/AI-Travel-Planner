[![CI](https://github.com/ArchanaChetan07/AI-Travel-Planner/actions/workflows/ci.yml/badge.svg)](https://github.com/ArchanaChetan07/AI-Travel-Planner/actions/workflows/ci.yml)

Agentic day-trip planner — **plan → tools → observe → revise(≤1) → finalize** loop, Streamlit UI, optional Groq LLM, Docker/K8s deployable.

**100% success across 40 DEMO_MODE runs · 60% revision rate · 0.001s avg latency (stub tools) · 54/54 tests · CI: green**

`DEMO_MODE=1 docker compose up --build` → open `http://localhost:8501` (no API key required).

**Repo:** [github.com/ArchanaChetan07/AI-Travel-Planner](https://github.com/ArchanaChetan07/AI-Travel-Planner)

---

## Overview

This is a real tool-loop agent for day-trip itineraries — not a single prompt chain:

1. **Plan** a Morning/Afternoon/Evening draft (DEMO templates or Groq Llama)
2. **Call tools** — `weather_hint`, `attractions_lookup`, `budget_check`
3. **Observe** weather/budget constraint failures
4. **Revise once** if outdoor weather or budget checks fail (`MAX_REVISIONS=1`)
5. **Finalize** Markdown with an agent-checks audit trail

---

## Agent loop design

```mermaid
flowchart LR
  P[Plan day] --> T[Call tools]
  T --> O[Observe]
  O -->|ok| F[Finalize]
  O -->|fail| R[Revise ≤1]
  R --> T2[Re-check tools]
  T2 --> F
```

| Stage | What happens |
|---|---|
| Plan | `generate_itinerary()` — DEMO templates offline; Groq when `DEMO_MODE=0` + key |
| Tools | Weather stub, curated attraction catalogue, budget estimator |
| Observe | `constraint_failures()` — rainy outdoor plan or over-budget estimate |
| Revise | One rewrite with indoor and/or cheap guidance, then re-run tools |
| Finalize | Append weather/budget/attractions audit block |

---

## Results (verified this session)

Command: `DEMO_MODE=1 python scripts/run_batch_eval.py --n 40`  
Artifact: [`artifacts/batch_metrics.json`](artifacts/batch_metrics.json)

| Metric | Value |
|---|---:|
| Mode | **DEMO_MODE** (no live APIs) |
| Batch size N | **40** |
| Success rate | **100.0%** (40/40 valid itineraries) |
| Revision rate | **60.0%** (24/40 used the 1 allowed revise) |
| Errors | **0** |
| Avg latency / loop | **0.0010 s** |
| p95 latency | **0.0015 s** |
| Hardware | Windows · Python 3.11.5 · CPU |

DEMO_MODE is intentionally fast (deterministic stubs). Live Groq latency was **not** measured in this session (no key exercised). The 60% revise rate is expected: rainy cities (Seattle/London/…) and tight budgets deliberately trigger the one-shot correction path.

Tests this session: **54/54 passed**.

---

## DEMO_MODE

| Env | Behavior |
|---|---|
| `DEMO_MODE=1` (default in Docker/CI) | Template itineraries + stub tools — **no Groq key** |
| `DEMO_MODE=0` + `GROQ_API_KEY` | Live Llama itinerary text; tools still offline stubs |
| Missing key | Auto-falls back to DEMO_MODE |

Toggle in `.env` (see `.env.example`).

---

## How to Run

```bash
git clone https://github.com/ArchanaChetan07/AI-Travel-Planner.git
cd AI-Travel-Planner
pip install -e .
cp .env.example .env   # DEMO_MODE=1 works with no key

streamlit run app.py
# or
DEMO_MODE=1 python scripts/run_batch_eval.py --n 40
```

Docker:

```bash
docker compose up --build
# Streamlit on :8501 (STREAMLIT_PORT=8503 if busy)
```

---

## Tests

```bash
DEMO_MODE=1 pytest tests/ -v
```

Covers planner validation, tools, agent revise/finalize, 20 parametrized cities, and batch metric shape.

---

## Tech Stack

| Layer | Tech |
|---|---|
| Agent | `src/agent/loop.py` |
| Tools | weather / attractions / budget stubs |
| LLM | Optional Groq Llama 3.3 |
| UI | Streamlit |
| Metrics | `src/eval/batch.py` |
| CI | GitHub Actions (DEMO_MODE, ruff, pytest, Docker build) |

---

## Deployment (K8s)

Manifest: [`k8s-deployment.yaml`](k8s-deployment.yaml) — Namespace, Deployment (`DEMO_MODE=1`), Service, HPA.

```bash
# Client-side validation (verified this session)
kubectl apply --dry-run=client -f k8s-deployment.yaml

# Live cluster (after building/pushing image as ai-travel-planner:latest)
kubectl apply -f k8s-deployment.yaml
```

Optional secret `travel-planner-secrets` may supply `GROQ_API_KEY`; omit it to stay offline.

---

## License

See repository.

## Author

**Archana Chetan** · [@ArchanaChetan07](https://github.com/ArchanaChetan07)
