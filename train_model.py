import logging
import os

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split

logger = logging.getLogger(__name__)


def train_tyre_degradation_model() -> None:
    logger.info("Initializing ML Training Pipeline...")

    file_path = "./feature_store/lap_times/monaco_2023_race_pace.parquet"
    try:
        df = pd.read_parquet(file_path)
        logger.info("Loaded %d rows from Data Lake.", len(df))
    except Exception as e:
        logger.error("Error loading Parquet file: %s", e)
        return

    ml_df = df[["LapTime_Seconds", "TyreLife", "Compound"]].dropna()

    all_compounds = ["HARD", "INTERMEDIATE", "MEDIUM", "SOFT", "WET"]
    ml_df["Compound"] = pd.Categorical(ml_df["Compound"], categories=all_compounds)
    ml_df = pd.get_dummies(ml_df, columns=["Compound"], drop_first=False)

    X = ml_df.drop(columns=["LapTime_Seconds"])
    y = ml_df["LapTime_Seconds"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    logger.info("Training Random Forest Regressor...")
    model = RandomForestRegressor(n_estimators=100, max_depth=5, random_state=42)
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    error = mean_absolute_error(y_test, predictions)
    logger.info(
        "Model MAE: %.3f seconds per lap.",
        error,
    )

    os.makedirs("./models", exist_ok=True)
    joblib.dump(model, "./models/tyre_deg_model.pkl")
    logger.info("Model saved to ./models/tyre_deg_model.pkl")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    train_tyre_degradation_model()
