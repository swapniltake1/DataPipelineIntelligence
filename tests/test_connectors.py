import pytest
from src.config import get_settings
from src.databricks_client import DatabricksClient
from src.azure_data_factory import AzureDataFactoryClient

def test_databricks_requires_https_host():
    with pytest.raises(ValueError):
        DatabricksClient("http://example.com", "fake-token")

def test_adf_requires_resource_settings():
    with pytest.raises(ValueError):
        AzureDataFactoryClient("", "rg", "factory")

def test_demo_mode_does_not_load_databricks_credentials(monkeypatch):
    monkeypatch.setenv("APP_MODE","demo")
    monkeypatch.setenv("DATABRICKS_FREE_HOST","https://example.com")
    monkeypatch.setenv("DATABRICKS_FREE_TOKEN","not-a-real-token")
    settings=get_settings()
    assert settings.app_mode=="demo"
    assert not settings.databricks_configured

def test_recovery_disabled_by_default(monkeypatch):
    monkeypatch.delenv("ENABLE_LIVE_RECOVERY",raising=False)
    assert get_settings().enable_live_recovery is False
