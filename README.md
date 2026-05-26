# F1 Intelligence Hub

**A full-stack Formula 1 data analytics and machine learning platform** that ingests real F1 telemetry via `fastf1`, trains a Random Forest model for lap time prediction, and serves an interactive race-engineering dashboard.

## Architecture

```
                         +---------------------------+
                         |   Next.js Frontend        |
                         |   (port 3000)             |
                         |   React 19 / Recharts     |
                         +-----------+---------------+
                                     |
                                   HTTP (REST)
                                     |
                         +-----------v---------------+
                         |   FastAPI Backend          |
                         |   (port 8000)             |
                         |   CORS for localhost:3000  |
                         +-----------+---------------+
                                     |
                    +----------------+----------------+
                    |                                 |
          +---------v--------+           +------------v-----------+
          | Feature Store    |           |  fastf1 API           |
          | (Parquet files)  |           |  (F1 live data)       |
          +------------------+           +------------------------+
                    |
          +---------v--------+
          | ML Model         |
          | tyre_deg_model   |
          | (Random Forest)  |
          +------------------+
```

## Features

| Feature | Description |
|---|---|
| **Pace Prediction** | ML-driven lap time forecast based on tyre compound and degradation |
| **Grid Telemetry** | High-resolution 10 Hz telemetry (speed, throttle, brake) per driver |
| **Circuit Analytics** | GPS track layout with speed heatmap, event info, and lap statistics |
| **Data Lake** | Parquet-based feature store with lazy-loading cache for instant replay |
| **Streamlit Dashboard** | Alternative Python-based UI for data exploration |

## Prerequisites

- **Python 3.11+**
- **Node.js 20+**
- **npm** or **yarn**

## Installation

### Backend

```bash
# Create a virtual environment
python -m venv .venv

# Activate it
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Frontend

```bash
cd f1-frontend
npm install
```

## Usage

### 1. Start the API server

```bash
python api.py
# or
uvicorn api:app --reload --port 8000
```

### 2. (Optional) Train the ML model

```bash
python train_model.py
```

### 3. Start the frontend

```bash
cd f1-frontend
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### 4. (Alternative) Streamlit dashboard

```bash
streamlit run app.py
```

## Data Pipeline

```bash
# Full ETL pipeline: ingest Monaco 2023, extract telemetry, save to feature store
python main.py

# Train degradation model on cleaned lap data
python train_model.py
```

Data is cached in `./f1_cache/` after first download. The feature store lives in `./feature_store/` as Parquet files for zero-latency replay.

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Health check |
| `GET` | `/schedule/{year}` | All circuit locations for a season |
| `GET` | `/circuit_info/{year}/{circuit}` | Official event metadata |
| `POST` | `/predict_pace` | Predict lap time (body: `{tyre_life, compound}`) |
| `GET` | `/telemetry/{year}/{circuit}/{driver}` | Driver's fastest lap telemetry |

### Predict Pace Example

```bash
curl -X POST http://localhost:8000/predict_pace \
  -H "Content-Type: application/json" \
  -d '{"tyre_life": 15, "compound": "SOFT"}'
```

Response:
```json
{
  "requested_compound": "SOFT",
  "tyre_life": 15,
  "predicted_lap_time_seconds": 75.234
}
```

## Project Structure

```
├── api.py                 # FastAPI REST API
├── app.py                 # Streamlit dashboard
├── main.py                # Data pipeline orchestrator
├── ingest_fastf1.py       # F1 data ingestion (fastf1 wrapper)
├── process_data.py        # ETL / data cleaning
├── train_model.py         # ML model training
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
├── f1-frontend/           # Next.js frontend application
│   ├── app/
│   │   ├── page.tsx       # Main dashboard (3 tabs)
│   │   ├── layout.tsx     # Root layout with Geist font
│   │   └── globals.css    # F1 design system
│   ├── package.json
│   └── README.md
│
├── CONTRIBUTING.md
├── LICENSE
└── README.md
```

## Tech Stack

### Backend
- **FastAPI** — REST API framework
- **fastf1** — Official F1 data API client
- **scikit-learn** — Random Forest Regressor
- **Pandas / NumPy** — Data processing
- **Joblib** — Model serialization
- **Streamlit** — Alternative Python dashboard

### Frontend
- **Next.js 16** — React framework
- **React 19** — UI library
- **Recharts** — Charts (line, area, scatter)
- **Tailwind CSS 4** — Utility-first styling
- **Lucide React** — Icon library

## License

MIT — see [LICENSE](LICENSE).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).
