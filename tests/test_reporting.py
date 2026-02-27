import pytest
from src.reporter import generate_daily_report
from pathlib import Path

@pytest.mark.integration
def test_daily_report_generation():
    txt_path, csv_path = generate_daily_report()

    assert isinstance(txt_path, Path)
    assert isinstance(csv_path, Path)

    assert txt_path.exists()
    assert csv_path.exists()

    content = txt_path.read_text(encoding="utf-8")
    assert "WEATHER DATA PIPELINE SYSTEM" in content