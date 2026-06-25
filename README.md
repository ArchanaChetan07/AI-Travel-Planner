# ✈️ AI Travel Itinerary Planner

> Generate personalised, AI-powered day-trip itineraries in seconds — powered by **LangChain**, **Groq**, and **Llama 3.3**.

[![CI](https://github.com/data-guru0/AI-TRAVEL-ITINEARY-PLANNER/actions/workflows/ci.yml/badge.svg)](https://github.com/data-guru0/AI-TRAVEL-ITINEARY-PLANNER/actions)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/docker-ready-blue?logo=docker)](Dockerfile)
[![Kubernetes](https://img.shields.io/badge/kubernetes-ready-326CE5?logo=kubernetes)](k8s-deployment.yaml)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Architecture](#️-architecture)
- [Project Structure](#-project-structure)
- [Quick Start](#-quick-start)
- [Configuration](#️-configuration)
- [Running Tests](#-running-tests)
- [Docker](#-docker)
- [Kubernetes Deployment](#☸️-kubernetes-deployment)
- [ELK Stack Observability](#-elk-stack-observability)
- [Tech Stack](#-tech-stack)
- [Contributing](#-contributing)

---

## 🌍 Overview

**AI Travel Itinerary Planner** is a Streamlit web application that accepts a city name and a list of personal interests, then uses a **Groq-hosted Llama 3.3 70B** language model via **LangChain** to generate a detailed, time-blocked day-trip itinerary — complete with venue recommendations and local food suggestions.

| Feature | Detail |
|---|---|
| 🤖 LLM | Llama 3.3 70B Versatile via Groq |
| ⚡ Inference Speed | ~300 tokens/s (Groq hardware) |
| 🖥️ UI | Streamlit (dark, responsive) |
| 📦 Containerised | Docker multi-stage build |
| ☸️ Orchestrated | Kubernetes with HPA |
| 📊 Observability | ELK Stack + Filebeat |
| ✅ Tested | Pytest + coverage |
| 🔄 CI/CD | GitHub Actions |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Streamlit UI                      │
│  ( app.py — form, pills, download, error handling )  │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│               TravelPlanner (core/planner.py)        │
│  • Validates inputs                                  │
│  • Manages conversation history (LangChain messages) │
│  • Delegates to the itinerary chain                  │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│           Itinerary Chain (chains/itinerary_chain.py)│
│  ChatPromptTemplate → ChatGroq → StrOutputParser     │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
              ┌─────────────────┐
              │  Groq API       │
              │  Llama 3.3 70B  │
              └─────────────────┘
```

---

## 📁 Project Structure

```
ai-travel-planner/
├── app.py                       # Streamlit entry point
├── Dockerfile                   # Multi-stage Docker build
├── k8s-deployment.yaml          # Kubernetes + HPA manifests
├── requirements.txt
├── setup.py
├── .env.example                 # Environment variable template
├── .gitignore
│
├── src/
│   ├── chains/
│   │   └── itinerary_chain.py   # LangChain prompt → Groq chain
│   ├── config/
│   │   └── config.py            # Env var loading & validation
│   ├── core/
│   │   └── planner.py           # TravelPlanner domain class
│   └── utils/
│       ├── logger.py            # Rotating file + stream logger
│       └── custom_exception.py  # TravelPlannerException
│
├── tests/
│   └── test_planner.py          # Pytest unit tests
│
├── .github/
│   └── workflows/
│       └── ci.yml               # GitHub Actions CI/CD
│
└── elk/                         # ELK Stack Kubernetes configs
    ├── elasticsearch.yaml
    ├── kibana.yaml
    ├── logstash.yaml
    └── filebeat.yaml
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- A free [Groq API key](https://console.groq.com)

### 1. Clone & install

```bash
git clone https://github.com/data-guru0/AI-TRAVEL-ITINEARY-PLANNER.git
cd AI-TRAVEL-ITINEARY-PLANNER
pip install -e .
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

### 3. Run the app

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## ⚙️ Configuration

All settings are loaded from environment variables (`.env` file or shell exports):

| Variable | Required | Default | Description |
|---|---|---|---|
| `GROQ_API_KEY` | ✅ | — | Groq API key from console.groq.com |
| `LLM_MODEL` | ❌ | `llama-3.3-70b-versatile` | Groq model name |
| `LLM_TEMPERATURE` | ❌ | `0.3` | Sampling temperature (0–1) |
| `LLM_MAX_TOKENS` | ❌ | `1024` | Max tokens in LLM response |
| `LOG_LEVEL` | ❌ | `INFO` | Python logging level |

---

## 🧪 Running Tests

```bash
# Install dev dependencies
pip install pytest pytest-cov

# Run all tests with coverage report
pytest tests/ -v --cov=src --cov-report=term-missing
```

Expected output:
```
tests/test_planner.py::TestSetCity::test_valid_city_is_stored     PASSED
tests/test_planner.py::TestSetCity::test_city_is_title_cased      PASSED
tests/test_planner.py::TestCreateItinerary::test_returns_itinerary_string  PASSED
...
---------- coverage: 94% ----------
```

---

## 🐳 Docker

### Build

```bash
docker build -t ai-travel-planner:latest .
```

### Run

```bash
docker run -p 8501:8501 \
  -e GROQ_API_KEY=your_key_here \
  ai-travel-planner:latest
```

Open [http://localhost:8501](http://localhost:8501).

---

## ☸️ Kubernetes Deployment

### Prerequisites

- A running Kubernetes cluster (Minikube, GKE, EKS, etc.)
- `kubectl` configured

### Deploy

```bash
# 1. Point Docker to your cluster's registry (Minikube example)
eval $(minikube docker-env)

# 2. Build the image inside the cluster
docker build -t streamlit-app:latest .

# 3. Create the API key secret
kubectl create secret generic travel-planner-secrets \
  --from-literal=GROQ_API_KEY="your_key_here"

# 4. Apply all manifests (namespace, deployment, service, HPA)
kubectl apply -f k8s-deployment.yaml

# 5. Verify
kubectl get pods -n travel-planner
kubectl get svc  -n travel-planner

# 6. Access the app
kubectl port-forward -n travel-planner svc/travel-planner-service 8501:80
```

The deployment includes:
- **2 replicas** by default for high availability
- **HorizontalPodAutoscaler** scaling from 2 → 6 pods at 70% CPU
- **Rolling updates** with zero downtime
- **Liveness & readiness probes** on `/health`
- **Resource requests/limits** to prevent noisy-neighbour issues
- **Non-root security context**

---

## 📊 ELK Stack Observability

Full log pipeline: `App → Filebeat → Logstash → Elasticsearch → Kibana`

### Setup

```bash
# 1. Create logging namespace
kubectl create namespace logging

# 2. Deploy ELK components (in order)
kubectl apply -f elk/elasticsearch.yaml
kubectl apply -f elk/kibana.yaml
kubectl apply -f elk/logstash.yaml
kubectl apply -f elk/filebeat.yaml

# 3. Wait for all pods to be Running
kubectl get pods -n logging -w

# 4. Access Kibana
kubectl port-forward -n logging svc/kibana 5601:5601
```

Open [http://localhost:5601](http://localhost:5601) → **Stack Management → Index Patterns** → create `filebeat-*` with `@timestamp`.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12 |
| LLM Framework | LangChain 0.3 |
| LLM Inference | Groq API (Llama 3.3 70B) |
| Web UI | Streamlit 1.40 |
| Containerisation | Docker (multi-stage) |
| Orchestration | Kubernetes + HPA |
| Logging | Python logging + RotatingFileHandler |
| Observability | ELK Stack + Filebeat |
| CI/CD | GitHub Actions |
| Testing | Pytest + pytest-cov |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/your-feature`
3. Commit your changes: `git commit -m "feat: add X"`
4. Push to the branch: `git push origin feat/your-feature`
5. Open a Pull Request

Please ensure all tests pass and coverage does not drop before submitting.


