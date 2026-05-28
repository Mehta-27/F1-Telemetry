import pytest
import pandas as pd
import numpy as np
import os
import joblib
from sklearn.ensemble import RandomForestRegressor


class TestModelTraining:
    @pytest.fixture
    def sample_ml_data(self, tmp_path):
        data = {
            "LapTime_Seconds": np.random.uniform(70, 90, 100),
            "TyreLife": np.random.randint(1, 30, 100),
            "Compound": np.random.choice(["SOFT", "MEDIUM", "HARD"], 100),
        }
        df = pd.DataFrame(data)
        os.makedirs(f"{tmp_path}/feature_store/lap_times", exist_ok=True)
        df.to_parquet(f"{tmp_path}/feature_store/lap_times/monaco_2023_race_pace.parquet")
        return tmp_path

    def test_model_trains_and_saves(self, sample_ml_data, monkeypatch):
        monkeypatch.chdir(sample_ml_data)
        from train_model import train_tyre_degradation_model
        train_tyre_degradation_model()
        assert os.path.exists("models/tyre_deg_model.pkl")

    def test_model_prediction_shape(self):
        model = RandomForestRegressor(n_estimators=10, max_depth=5, random_state=42)
        X = pd.DataFrame({
            "TyreLife": [1, 2, 3],
            "Compound_HARD": [0, 0, 0],
            "Compound_INTERMEDIATE": [0, 0, 0],
            "Compound_MEDIUM": [0, 0, 1],
            "Compound_SOFT": [1, 1, 0],
            "Compound_WET": [0, 0, 0],
        })
        y = [75.0, 76.0, 77.0]
        model.fit(X, y)
        pred = model.predict(X)
        assert pred.shape == (3,)
