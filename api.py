from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import joblib
import os
import fastf1
import threading

from ingest_fastf1 import F1DataIngestor
from process_data import get_fastest_lap_telemetry, save_to_feature_store

app = FastAPI(title="F1 Intelligence Hub API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://f1telemetry.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ingestor = F1DataIngestor()

model_path = './models/tyre_deg_model.pkl'
if os.path.exists(model_path):
    model = joblib.load(model_path)
    print("System: ML Model loaded into server memory.")
else:
    print("Warning: Model not found. Did you run train_model.py?")
    model = None

class PredictionRequest(BaseModel):
    tyre_life: int
    compound: str

@app.get("/")
def health_check():
    return {"status": "Online", "service": "F1 Intelligence Core"}

@app.get("/schedule/{year}")
def get_schedule(year: int):
    try:
        schedule = fastf1.get_event_schedule(year)
        races = schedule[schedule['RoundNumber'] > 0]
        return {"circuits": races['Location'].tolist()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/circuit_info/{year}/{circuit_name}")
def get_circuit_info_dynamic(year: int, circuit_name: str):
    try:
        schedule = fastf1.get_event_schedule(year)
        event = schedule[schedule['Location'].str.contains(circuit_name, case=False, na=False)]
        if event.empty:
            raise HTTPException(status_code=404, detail="Circuit not found for this year.")
        event_data = event.iloc[0]
        return {
            "Official Event Name": event_data['EventName'],
            "Location": event_data['Location'],
            "Country": event_data['Country'],
            "Event Date": str(event_data['EventDate'].date()),
            "Weekend Format": event_data['EventFormat']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict_pace")
def predict_lap_pace(request: PredictionRequest):
    if model is None:
        raise HTTPException(status_code=500, detail="ML Model is offline.")

    compound = request.compound.upper()
    valid_compounds = ['HARD', 'MEDIUM', 'SOFT', 'INTERMEDIATE', 'WET']

    if compound not in valid_compounds:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid compound. Use {', '.join(valid_compounds)}."
        )

    expected_columns = model.feature_names_in_.tolist() if hasattr(model, 'feature_names_in_') else None
    if expected_columns is None:
        raise HTTPException(status_code=500, detail="Model has no feature_names_in_ attribute. Please retrain the model.")

    input_data = {'TyreLife': [request.tyre_life]}
    compound_col = f'Compound_{compound}'
    for col in expected_columns:
        if col != 'TyreLife':
            input_data[col] = [1 if col == compound_col else 0]

    ml_df = pd.DataFrame(input_data)
    ml_df = ml_df[expected_columns]

    prediction = model.predict(ml_df)[0]

    return {
        "requested_compound": compound,
        "tyre_life": request.tyre_life,
        "predicted_lap_time_seconds": round(prediction, 3)
    }

@app.get("/telemetry/{year}/{circuit}/{driver}")
def get_dynamic_telemetry(year: int, circuit: str, driver: str):
    driver = driver.upper()
    circuit = circuit.strip()

    file_name = f"{circuit}_{year}_{driver}_fastest"
    file_path = f'./feature_store/telemetry/{file_name}.parquet'

    if os.path.exists(file_path):
        print(f"Server: Cache Hit for {file_name}. Serving instantly.")
        df = pd.read_parquet(file_path)
        return df.to_dict(orient="records")

    print(f"Server: Cache Miss for {file_name}. Downloading...")

    try:
        laps_df, weather_df = ingestor.get_race_data(year, circuit, 'R')
        if laps_df is None:
            raise HTTPException(status_code=404, detail="Race data not found on F1 servers.")

        telemetry = get_fastest_lap_telemetry(laps_df, driver)
        if telemetry is None:
            raise HTTPException(status_code=404, detail=f"No telemetry found for {driver}.")

        save_to_feature_store(telemetry, 'telemetry', file_name)

        return telemetry.to_dict(orient="records")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
