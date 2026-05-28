import pytest
import pandas as pd
from process_data import clean_race_laps, get_fastest_lap_telemetry, save_to_feature_store


class TestCleanRaceLaps:
    def test_clean_laps_removes_inaccurate(self, sample_laps_df):
        df = sample_laps_df.copy()
        df.loc[0, "IsAccurate"] = False
        result = clean_race_laps(df)
        assert len(result) < len(df)

    def test_clean_laps_returns_expected_columns(self, sample_laps_df):
        result = clean_race_laps(sample_laps_df)
        expected = ["Driver", "LapNumber", "LapTime_Seconds", "Compound", "TyreLife", "Stint"]
        assert all(col in result.columns for col in expected)

    def test_clean_laps_converts_timedelta(self, sample_laps_df):
        result = clean_race_laps(sample_laps_df)
        assert result["LapTime_Seconds"].dtype == "float64"

    def test_clean_laps_drops_pit_laps(self, sample_laps_df):
        df = sample_laps_df.copy()
        df.loc[0, "PitInTime"] = pd.Timestamp("2023-01-01 12:00:00")
        result = clean_race_laps(df)
        assert len(result) == len(df) - 1


class TestGetFastestLapTelemetry:
    def test_returns_none_on_invalid_input(self):
        result = get_fastest_lap_telemetry(None, "VER")
        assert result is None


class TestSaveToFeatureStore:
    def test_saves_parquet(self, sample_telemetry, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        import os
        os.makedirs("feature_store/telemetry", exist_ok=True)
        save_to_feature_store(sample_telemetry, "telemetry", "test_driver")
        assert os.path.exists("feature_store/telemetry/test_driver.parquet")
