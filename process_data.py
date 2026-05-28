import logging
import os
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)


def clean_race_laps(laps_df: pd.DataFrame) -> pd.DataFrame:
    clean_df = laps_df[laps_df["IsAccurate"] == True].copy()
    clean_df = clean_df[
        (clean_df["PitOutTime"].isnull()) & (clean_df["PitInTime"].isnull())
    ]
    clean_df["LapTime_Seconds"] = clean_df["LapTime"].dt.total_seconds()
    features = ["Driver", "LapNumber", "LapTime_Seconds", "Compound", "TyreLife", "Stint"]
    clean_df = clean_df[features]
    clean_df = clean_df.dropna(subset=["LapTime_Seconds"])
    logger.info("Filtered down to %d pure racing laps.", len(clean_df))
    return clean_df


def get_fastest_lap_telemetry(
    raw_laps_df, driver_code: str
) -> Optional[pd.DataFrame]:
    logger.info("Extracting high-res telemetry for %s...", driver_code)
    try:
        fastest_lap = raw_laps_df.pick_drivers(driver_code).pick_fastest()
        telemetry = fastest_lap.get_telemetry()
        telemetry["Driver"] = driver_code
        features = ["Driver", "Distance", "Speed", "Throttle", "Brake", "nGear", "RPM", "X", "Y"]
        clean_telemetry = telemetry[features]
        logger.info("Extracted %d data points for %s.", len(clean_telemetry), driver_code)
        return clean_telemetry
    except Exception as e:
        logger.error("Error extracting telemetry for %s: %s", driver_code, e)
        return None


def save_to_feature_store(df: pd.DataFrame, folder_name: str, file_name: str) -> None:
    store_path = f"./feature_store/{folder_name}"
    os.makedirs(store_path, exist_ok=True)
    full_path = f"{store_path}/{file_name}.parquet"
    df.to_parquet(full_path, index=False)
    logger.info("Saved data to %s", full_path)