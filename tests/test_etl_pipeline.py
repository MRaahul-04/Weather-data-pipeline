import pytest
from src.etl_pipeline import WeatherETLPipeline

@pytest.mark.integration
def test_etl_pipeline_initialization():
    pipeline = WeatherETLPipeline()
    assert pipeline.api_client is not None
