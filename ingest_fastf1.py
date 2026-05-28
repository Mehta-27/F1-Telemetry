import logging
import os
from typing import Optional

import fastf1
import pandas as pd

logger = logging.getLogger(__name__)


class F1DataIngestor:
    def __init__(self, cache_dir: str = "./f1_cache") -> None:
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)
        fastf1.Cache.enable_cache(self.cache_dir)
        logger.info("fastf1 cache enabled at %s", self.cache_dir)

    def get_race_data(
        self, year: int, circuit: str, session_type: str = "R"
    ) -> tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]:
        logger.info("Fetching data for %d %s (%s)...", year, circuit, session_type)
        try:
            session = fastf1.get_session(year, circuit, session_type)
            session.load(telemetry=True, weather=True, messages=False)
            laps_df = session.laps
            weather_df = session.weather_data
            logger.info("Loaded %d laps.", len(laps_df))
            return laps_df, weather_df
        except Exception as e:
            logger.error("Error fetching data: %s", e)
            return None, None

# Run the ingestion
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    ingestor = F1DataIngestor()
    monaco_laps, monaco_weather = ingestor.get_race_data(2023, "Monaco", "R")
    if monaco_laps is not None:
        logger.info(
            "Raw preview:\n%s",
            monaco_laps[["Driver", "LapTime", "Compound", "TyreLife"]].head(3),
        )