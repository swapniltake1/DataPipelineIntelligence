"""Read-first Databricks Jobs API client."""
from datetime import datetime, timezone
from typing import Any
import requests

class DatabricksAPIError(RuntimeError):
    pass

class DatabricksClient:
    def __init__(self, host: str, token: str, timeout: int = 20):
        if not host or not token:
            raise ValueError("Databricks host and token are required.")
        if not host.startswith("https://"):
            raise ValueError("Databricks host must start with https://.")
        self.host, self.timeout = host.rstrip("/"), timeout
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {token}", "Content-Type": "application/json"})

    def _request(self, method: str, path: str, **kwargs: Any) -> dict:
        try:
            response = self.session.request(method, f"{self.host}{path}", timeout=self.timeout, **kwargs)
        except requests.RequestException as exc:
            raise DatabricksAPIError(f"Databricks connection failed: {exc}") from exc
        if not response.ok:
            raise DatabricksAPIError(f"Databricks API returned HTTP {response.status_code}: {response.text[:600]}")
        if not response.content:
            return {}
        try:
            return response.json()
        except ValueError as exc:
            raise DatabricksAPIError("Databricks returned a non-JSON response.") from exc

    def list_jobs(self, limit: int = 100) -> list[dict]:
        return self._request("GET", "/api/2.2/jobs/list", params={"limit": min(max(limit, 1), 100)}).get("jobs", [])

    def list_runs(self, limit: int = 50) -> list[dict]:
        payload = self._request("GET", "/api/2.2/jobs/runs/list", params={"limit": min(max(limit, 1), 100), "expand_tasks": "true"})
        normalized = []
        for item in payload.get("runs", []):
            state = item.get("state") or {}
            result = state.get("result_state") or ""
            lifecycle = state.get("life_cycle_state") or "UNKNOWN"
            if result == "SUCCESS": status = "Succeeded"
            elif lifecycle in {"PENDING", "QUEUED", "RUNNING", "TERMINATING", "WAITING_FOR_RETRY"}: status = "Running"
            elif lifecycle == "SKIPPED": status = "Skipped"
            elif result in {"FAILED", "TIMEDOUT", "CANCELED", "MAXIMUM_CONCURRENT_RUNS_REACHED"}: status = "Failed"
            else: status = "Failed" if lifecycle == "INTERNAL_ERROR" else lifecycle.title()
            start_ms = item.get("start_time", 0)
            errors = [str((t.get("state") or {}).get("state_message")) for t in item.get("tasks", []) or [] if (t.get("state") or {}).get("state_message")]
            normalized.append({
                "run_id": str(item.get("run_id", "")), "job_id": item.get("job_id"),
                "pipeline": item.get("run_name") or f"Databricks job {item.get('job_id', 'unknown')}",
                "status": status, "duration_minutes": max(0, int(item.get("run_duration", 0) / 60000)),
                "started_at": datetime.fromtimestamp(start_ms / 1000, tz=timezone.utc).isoformat() if start_ms else "",
                "error": " | ".join(errors) or (state.get("state_message", "") if status == "Failed" else ""),
                "retry_count": max(0, int(item.get("attempt_number", 1) or 1) - 1),
                "source": "Databricks", "raw_lifecycle_state": lifecycle, "raw_result_state": result})
        return normalized
