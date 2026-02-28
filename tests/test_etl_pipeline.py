# Integration tests for the ETL pipeline

# Importing the pytest testing framework
import pytest
# Importing the ETL component under test
from src.etl_pipeline import WeatherETLPipeline

# This test is categorized as an integration test
@pytest.mark.integration
# Validates successful pipeline initialization
def test_etl_pipeline_initialization():
    pipeline = WeatherETLPipeline()
    assert pipeline.api_client is not None
