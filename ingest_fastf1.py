import fastf1
import os
import pandas as pd

class F1DataIngestor:
    def __init__(self, cache_dir='./f1_cache'):
        """
        Initializes the ingestor and strictly enforces caching.
        """
        self.cache_dir = cache_dir
        
        # 1. The Golden Rule: Enable Caching
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        fastf1.Cache.enable_cache(self.cache_dir)
        print(f"System: fastf1 cache enabled at {self.cache_dir}")

    def get_race_data(self, year: int, circuit: str, session_type: str = 'R'):
        """
        Downloads and loads all telemetry, laps, and weather for a specific session.
        session_type: 'FP1', 'FP2', 'FP3', 'Q' (Qualifying), 'R' (Race)
        """
        print(f"System: Fetching data for {year} {circuit} ({session_type})...")
        
        # 2. Fetch the Session
        try:
            session = fastf1.get_session(year, circuit, session_type)
            
            # 3. Load the data (This takes time on the first run, but is instant afterward)
            session.load(telemetry=True, weather=True, messages=False)
            
            # Extract the core DataFrames
            laps_df = session.laps
            weather_df = session.weather_data
            
            print(f"Success: Loaded {len(laps_df)} laps.")
            return laps_df, weather_df
            
        except Exception as e:
            print(f"Error fetching data: {e}")
            return None, None

# Run the ingestion
if __name__ == "__main__":
    ingestor = F1DataIngestor()
    
    # Let's pull the 2023 Monaco Grand Prix Race
    monaco_laps, monaco_weather = ingestor.get_race_data(2023, 'Monaco', 'R')
    
    # Preview the raw data
    if monaco_laps is not None:
        print("\nRaw Data Preview (First 3 laps):")
        print(monaco_laps[['Driver', 'LapTime', 'Compound', 'TyreLife']].head(3))