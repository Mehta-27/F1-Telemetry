import os
import sys
import time
import fastf1
import pandas as pd
from process_data import get_fastest_lap_telemetry, save_to_feature_store

YEARS = [2024, 2023, 2022, 2021, 2020, 2019, 2018]
GRID = ["VER","HAM","ALO","LEC","SAI","NOR","PIA","RUS","PER","OCO","BOT","MAG","ALB","TSU","STR","ZHO","HUL","SAR"]
CACHE_DIR = "./f1_cache"
TELEMETRY_DIR = "./feature_store/telemetry"
os.makedirs(TELEMETRY_DIR, exist_ok=True)

fastf1.Cache.enable_cache(CACHE_DIR)

def get_all_events(year):
    schedule = fastf1.get_event_schedule(year)
    return schedule[schedule['RoundNumber'] > 0]

def file_exists(year, circuit, driver):
    fname = f"{circuit}_{year}_{driver}_fastest.parquet"
    return os.path.exists(os.path.join(TELEMETRY_DIR, fname))

total = 0
skipped = 0
downloaded = 0
failed = 0

for year in YEARS:
    print(f"\n{'='*60}")
    print(f"YEAR: {year}")
    print(f"{'='*60}")
    try:
        events = get_all_events(year)
    except Exception as e:
        print(f"  Failed to fetch schedule for {year}: {e}")
        continue

    for _, event in events.iterrows():
        circuit = event['Location']
        round_num = event['RoundNumber']
        print(f"\n  Circuit: {circuit} (Round {round_num})")

        try:
            session = fastf1.get_session(year, round_num, 'R')
            session.load()
            laps = session.laps
        except Exception as e:
            print(f"    Failed to load session: {e}")
            continue

        available = set()
        try:
            dds = session.driver_info
            available = {d.Abbreviation for d in dds if hasattr(d, 'Abbreviation')}
        except:
            available = set(GRID)

        for driver in GRID:
            total += 1
            if driver not in available:
                skipped += 1
                continue
            if file_exists(year, circuit, driver):
                skipped += 1
                continue

            try:
                driver_laps = laps.pick_drivers(driver)
                if driver_laps.empty:
                    continue

                fastest = driver_laps.pick_fastest()
                if fastest is None:
                    continue

                telemetry = fastest.get_telemetry()
                if telemetry is None or telemetry.empty:
                    continue

                telemetry['Driver'] = driver
                fname = f"{circuit}_{year}_{driver}_fastest"
                save_to_feature_store(telemetry, 'telemetry', fname)
                downloaded += 1
                print(f"    OK {driver} downloaded")
                time.sleep(0.5)

            except Exception as e:
                failed += 1
                print(f"    FAIL {driver}: {str(e)[:60]}")
                continue

print(f"\n{'='*60}")
print(f"COMPLETE: Total={total}, Downloaded={downloaded}, Skipped={skipped}, Failed={failed}")
print(f"{'='*60}")
