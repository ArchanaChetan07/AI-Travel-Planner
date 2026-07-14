# AI Travel Planning Agent

> A **tool-loop planning agent** for day-trip itineraries: plan → call tools → observe → revise once if weather/budget fails → finalize. Streamlit UI; optional Groq LLM; full **DEMO_MODE** offline.

[![CI](https://github.com/ArchanaChetan07/AI-Travel-Planner/actions/workflows/ci.yml/badge.svg)](https://github.com/ArchanaChetan07/AI-Travel-Planner/actions)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/docker-ready-blue?logo=docker)](Dockerfile)
[![Kubernetes](https://img.shields.io/badge/kubernetes-ready-326CE5?logo=kubernetes)](k8s-deployment.yaml)

---

## Overview

This is not a single prompt chain dressed up as an “agent.” The core loop in `src/agent/loop.py` actually:

1. **Plans** a day-trip itinerary (Groq Llama when a key is present, else DEMO templates)
2. **Calls tools** — `weather_hint`, `attractions_lookup`, `budget_check`
3. **Observes** weather/budget constraint failures
4. **Revises once** if outdoor weather or budget checks fail
5. **Finalizes** Markdown with an agent-checks audit trail

| Feature | Detail |
|---|---|
| Agent loop | plan → tools → observe → revise (≤1) → finalize |
| Tools | weather stub, curated attractions, budget estimator |
| DEMO_MODE | Offline templates + tools (no API key) |
| Optional LLM | Groq Llama 3.3 when `GROQ_API_KEY` is set and `DEMO_MODE=0` |
| UI | Streamlit |
| Packaging | Docker + Kubernetes manifests |
| CI | GitHub Actions (strict, DEMO_MODE, pytest + ruff) |

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Streamlit UI                      │
│         (app.py — city, interests, budget)           │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│               TravelPlanner (core/planner.py)        │
│  validates inputs → run_planning_loop()              │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│            Agent loop (agent/loop.py)                │
│  plan day → tools → observe → revise once → finalize │
└───────────┬─────────────────────────────┬───────────┘
            │                             │
            ▼                             ▼
┌───────────────────────┐   ┌──────────────────────────┐
│ itinerary_chain.py    │   │ tools/registry.py         │
│ DEMO template or Groq │   │ weather_hint              │
│                       │   │ attractions_lookup        │
│                       │   │ budget_check              │
└───────────────────────┘   └──────────────────────────┘
```

---

## Project Structure

```
AI-Travel-Planner/
├── app.py                       # Streamlit entry point
├── Dockerfile
├── k8s-deployment.yaml
├── requirements.txt
├── setup.py
├── .env.example
├── src/
│   ├── agent/
│   │   ├── loop.py              # Tool-loop planning agent
│   │   └── types.py
│   ├── tools/
│   │   └── registry.py          # weather / attractions / budget
│   ├── chains/
│   │   └── itinerary_chain.py   # DEMO templates + optional Groq
│   ├── config/
│   │   └── config.py
│   ├── core/
│   │   └── planner.py           # TravelPlanner façade
│   └── utils/
├── tests/
│   ├── conftest.py              # Forces DEMO_MODE offline
│   └── test_planner.py
└── .github/workflows/ci.yml
```

---

## Quick Start

### Prerequisites

- Python 3.10+
- Optional: a free [Groq API key](https://console.groq.com) for live LLM mode

### 1. Clone & install

```bash
git clone https://github.com/ArchanaChetan07/AI-Travel-Planner.git
cd AI-Travel-Planner
pip install -e .
```

### 2. Configure environment

```bash
cp .env.example .env
# DEMO_MODE=1 works with no key. For live LLM: set GROQ_API_KEY and DEMO_MODE=0
```

### 3. Run the app

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501).

---

## Configuration

| Variable | Required | Default | Description |
|---|---|---|---|
| `DEMO_MODE` | ❌ | auto if no key | `1`/`true` forces offline templates + stub tools |
| `GROQ_API_KEY` | ❌ in DEMO | — | Groq API key for live itinerary text |
| `LLM_MODEL` | ❌ | `llama-3.3-70b-versatile` | Groq model name |
| `LLM_TEMPERATURE` | ❌ | `0.3` | Sampling temperature |
| `LLM_MAX_TOKENS` | ❌ | `1024` | Max tokens |
| `DEFAULT_BUDGET_USD` | ❌ | `150` | Default day budget |
| `LOG_LEVEL` | ❌ | `INFO` | Logging level |

---

## Running Tests

```bash
pip install pytest pytest-cov ruff
pytest tests/ -v --cov=src --cov-report=term-missing
ruff check src/ tests/
```

CI runs the same suite with `DEMO_MODE=1` (no network, no secrets).

---

## Docker

```bash
docker build -t ai-travel-planner:latest .
docker run -p 8501:8501 -e DEMO_MODE=1 ai-travel-planner:latest
# or live: -e DEMO_MODE=0 -e GROQ_API_KEY=your_key_here
```

---

## Kubernetes Deployment

```bash
eval $(minikube docker-env)   # if using Minikube
docker build -t streamlit-app:latest .

kubectl create secret generic travel-planner-secrets \
  --from-literal=GROQ_API_KEY="your_key_here" \
  --from-literal=DEMO_MODE="0"

kubectl apply -f k8s-deployment.yaml
kubectl get pods -n travel-planner
kubectl port-forward -n travel-planner svc/travel-planner-service 8501:80
```

Manifests keep replicas, HPA, probes, and non-root security context.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| Agent | Custom plan → tool → observe → revise loop |
| Optional LLM | LangChain + Groq (Llama 3.3) |
| Web UI | Streamlit |
| Containers | Docker + Kubernetes |
| CI | GitHub Actions (pytest + ruff, DEMO_MODE) |

---

## Contributing

1. Fork and branch
2. Keep tests green under `DEMO_MODE=1`
3. Open a PR
