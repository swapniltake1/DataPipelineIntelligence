"""Environment-driven configuration for demo, Databricks Free Edition and Azure."""
from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()

def _bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}

@dataclass(frozen=True)
class Settings:
    app_mode: str
    databricks_host: str
    databricks_token: str
    azure_subscription_id: str
    azure_resource_group: str
    azure_data_factory_name: str
    azure_access_token: str
    azure_management_api_version: str
    enable_live_recovery: bool
    max_automatic_retries: int
    request_timeout_seconds: int
    audit_log_path: str
    @property
    def databricks_configured(self) -> bool:
        return bool(self.databricks_host and self.databricks_token)
    @property
    def adf_configured(self) -> bool:
        return bool(self.azure_subscription_id and self.azure_resource_group and self.azure_data_factory_name)

def get_settings() -> Settings:
    mode = os.getenv("APP_MODE", "demo").strip().lower()
    if mode not in {"demo", "free", "azure"}:
        mode = "demo"
    if mode == "free":
        host = os.getenv("DATABRICKS_FREE_HOST") or os.getenv("DATABRICKS_HOST", "")
        token = os.getenv("DATABRICKS_FREE_TOKEN") or os.getenv("DATABRICKS_TOKEN", "")
    elif mode == "azure":
        host = os.getenv("AZURE_DATABRICKS_HOST") or os.getenv("DATABRICKS_HOST", "")
        token = os.getenv("AZURE_DATABRICKS_TOKEN") or os.getenv("DATABRICKS_TOKEN", "")
    else:
        host, token = "", ""
    return Settings(mode, host.strip().rstrip("/"), token.strip(),
        os.getenv("AZURE_SUBSCRIPTION_ID", "").strip(), os.getenv("AZURE_RESOURCE_GROUP", "").strip(),
        os.getenv("AZURE_DATA_FACTORY_NAME", "").strip(), os.getenv("AZURE_ACCESS_TOKEN", "").strip(),
        os.getenv("AZURE_MANAGEMENT_API_VERSION", "2018-06-01").strip(),
        _bool("ENABLE_LIVE_RECOVERY", False), max(0, int(os.getenv("MAX_AUTOMATIC_RETRIES", "0"))),
        max(5, int(os.getenv("REQUEST_TIMEOUT_SECONDS", "20"))), os.getenv("AUDIT_LOG_PATH", "logs/audit.jsonl").strip())
