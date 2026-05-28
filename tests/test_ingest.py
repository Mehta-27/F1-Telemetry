import pytest
from ingest_fastf1 import F1DataIngestor


class TestF1DataIngestor:
    def test_init_creates_cache_dir(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        ingestor = F1DataIngestor(cache_dir=str(tmp_path / "f1_cache"))
        assert (tmp_path / "f1_cache").exists()

    def test_get_race_data_returns_none_on_bad_session(self):
        ingestor = F1DataIngestor(cache_dir="./test_cache_bad")
        laps, weather = ingestor.get_race_data(1999, "NonExistent", "R")
        assert laps is None
        assert weather is None
