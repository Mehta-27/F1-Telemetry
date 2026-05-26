from ingest_fastf1 import F1DataIngestor
from process_data import clean_race_laps, get_fastest_lap_telemetry, save_to_feature_store

if __name__ == "__main__":
    ingestor = F1DataIngestor()
    monaco_laps, monaco_weather = ingestor.get_race_data(2023, 'Monaco', 'R')

    if monaco_laps is None:
        print("Error: Failed to fetch race data. Exiting.")
        exit(1)

    print("System: Extracting grid telemetry...")

    all_drivers = monaco_laps['Driver'].unique()

    for driver in all_drivers:
        telemetry = get_fastest_lap_telemetry(monaco_laps, driver)
        if telemetry is not None:
            save_to_feature_store(telemetry, 'telemetry', f'monaco_2023_{driver}_fastest')

    print("\nPipeline Execution Complete! Your Data Lake is populated.")
