# Integration tests for report generation functionality

# Testing framework used
import pytest
# Function under test
from src.reporter import generate_daily_report
from pathlib import Path

# This test validates end-to-end report creation
@pytest.mark.integration
# Verifies both TXT and CSV reports are generated correctly
def test_daily_report_generation():
    # Unpacking returned report paths
    txt_path, csv_path = generate_daily_report()

    # Validating path types
    assert isinstance(txt_path, Path)
    assert isinstance(csv_path, Path)

    # Checking file existence
    assert txt_path.exists()
    assert csv_path.exists()

    # Reading and validating report content
    content = txt_path.read_text(encoding="utf-8")
    assert "WEATHER DATA PIPELINE SYSTEM" in content