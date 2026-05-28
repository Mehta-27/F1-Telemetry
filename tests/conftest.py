import pytest
import pandas as pd
import numpy as np


@pytest.fixture
def sample_telemetry():
    return pd.DataFrame({
        "Distance": np.linspace(0, 5000, 100),
        "Speed": np.random.uniform(100, 320, 100),
        "Throttle": np.random.uniform(0, 100, 100),
        "Brake": np.random.uniform(0, 100, 100),
        "nGear": np.random.randint(1, 9, 100),
        "RPM": np.random.uniform(8000, 12000, 100),
        "X": np.random.uniform(-200, 200, 100),
        "Y": np.random.uniform(-200, 200, 100),
        "Driver": ["VER"] * 100,
    })


@pytest.fixture
def sample_laps_df():
    return pd.DataFrame({
        "Driver": ["VER", "HAM", "VER", "HAM"],
        "LapNumber": [1, 1, 2, 2],
        "LapTime": pd.to_timedelta(["1:15.5", "1:16.0", "1:14.8", "1:15.2"]),
        "Compound": ["SOFT", "SOFT", "MEDIUM", "MEDIUM"],
        "TyreLife": [1, 1, 2, 2],
        "Stint": [1, 1, 1, 1],
        "IsAccurate": [True, True, True, True],
        "PitOutTime": [None, None, None, None],
        "PitInTime": [None, None, None, None],
    })
