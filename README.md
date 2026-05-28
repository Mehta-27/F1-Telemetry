<div align="center">
  <img src="https://img.shields.io/badge/Python-3.11%2B-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/Streamlit-1.57-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit 1.57">
  <img src="https://img.shields.io/badge/scikit--learn-1.8-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white" alt="scikit-learn 1.8">
  <img src="https://img.shields.io/badge/fastf1-3.8-FF1801?style=for-the-badge" alt="fastf1 3.8">
  <br>
  <img src="https://img.shields.io/github/actions/workflow/status/Mehta-27/F1-Telemetry/ci.yml?style=for-the-badge&label=CI&logo=github" alt="CI">
  <img src="https://img.shields.io/github/license/Mehta-27/F1-Telemetry?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/github/stars/Mehta-27/F1-Telemetry?style=for-the-badge&logo=github" alt="Stars">
  <img src="https://img.shields.io/badge/code%20style-ruff-000000?style=for-the-badge" alt="Ruff">
</div>

<h1 align="center">
  F1 Intelligence Hub
</h1>

<p align="center">
  <b>Formula 1 data analytics &amp; ML platform</b> — Ingest real F1 telemetry via <code>fastf1</code>, train a Random Forest model for lap time prediction, and explore data through a cinematic Streamlit dashboard.
</p>

<p align="center">
  <a href="#-features">Features</a> ·
  <a href="#-quick-start">Quick Start</a> ·
  <a href="#-project-structure">Structure</a> ·
  <a href="#-tech-stack">Tech Stack</a> ·
  <a href="#-contributing">Contributing</a>
</p>

---

## Features

| Feature | Description |
|---|---|
| **Pace Prediction** | ML-driven lap time forecast based on tyre compound & degradation |
| **Grid Telemetry** | High-resolution 10 Hz telemetry (speed, throttle, brake) per driver |
| **Circuit Analytics** | GPS track layout with speed heatmap, event info, and lap statistics |
| **Data Lake** | Parquet-based feature store with lazy-loading cache for instant replay |
| **Docker Support** | Single-command deployment with `docker compose up` |
| **CI/CD** | Automated linting, type checking, testing via GitHub Actions |

## Quick Start

### Option 1: Docker (recommended)

```bash
docker compose up
```

Open [http://localhost:8501](http://localhost:8501).

### Option 2: Native

```bash
# 1. Create virtual environment
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch dashboard
streamlit run app.py
```

### Train the ML Model

```bash
python train_model.py
```

## Data Pipeline

```
fastf1 API  ──▶  ingest_fastf1.py  ──▶  process_data.py  ──▶  feature_store/  ──▶  train_model.py
                                                                                      │
                                                                                      ▼
                                                                              models/tyre_deg_model.pkl
```

Data is cached in `./f1_cache/` after first download. Feature store lives in `./feature_store/` as Parquet files for zero-latency replay.

## Project Structure

```
├── app.py                 # Streamlit dashboard (cinematic F1 UI)
├── ingest_fastf1.py       # F1 data ingestion (fastf1 wrapper)
├── process_data.py        # ETL / data cleaning
├── train_model.py         # ML model training (Random Forest)
├── requirements.txt       # Python dependencies
│
├── models/
│   └── tyre_deg_model.pkl # Trained Random Forest model
│
├── feature_store/
│   ├── lap_times/         # Cleaned lap data (Parquet)
│   └── telemetry/         # High-res telemetry (Parquet)
│
├── f1_cache/              # fastf1 HTTP cache (auto-generated)
│
├── tests/                 # Pytest test suite
│   ├── conftest.py
│   ├── test_ingest.py
│   ├── test_process.py
│   └── test_train.py
│
├── .github/
│   ├── workflows/ci.yml   # GitHub Actions CI
│   ├── ISSUE_TEMPLATE/    # Bug report & feature request templates
│   └── PULL_REQUEST_TEMPLATE.md
│
├── Dockerfile             # Production container image
├── docker-compose.yml     # Orchestrated deployment
├── pyproject.toml         # Project metadata & tool config
├── Makefile               # Common dev commands
├── .pre-commit-config.yaml
├── .editorconfig
├── SECURITY.md
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── LICENSE
└── README.md
```

## Tech Stack

| Layer | Technology |
|---|---|
| **Language** | Python 3.11+ |
| **Dashboard** | Streamlit |
| **Data** | fastf1, Pandas, NumPy |
| **ML** | scikit-learn (Random Forest), Joblib |
| **Viz** | Altair |
| **Infra** | Docker, docker-compose, GitHub Actions |
| **Quality** | Ruff, mypy, pytest, pre-commit |

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for our guidelines.

## License

MIT — see [LICENSE](LICENSE).
