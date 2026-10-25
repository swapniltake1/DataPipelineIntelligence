"""Optional Azure Data Factory pipeline-run monitor using ARM REST API."""
from datetime import datetime, timedelta, timezone
import requests

class AzureDataFactoryError(RuntimeError):
    pass

class AzureDataFactoryClient:
    def __init__(self, subscription_id: str, resource_group: str, factory_name: str, access_token: str = "", api_version: str = "2018-06-01", timeout: int = 20):
        self.subscription_id, self.resource_group, self.factory_name = subscription_id, resource_group, factory_name
        self.access_token, self.api_version, self.timeout = access_token, api_version, timeout
        if not all((subscription_id, resource_group, factory_name)):
            raise ValueError("Azure subscription, resource group, and Data Factory name are required.")

    def _get_token(self):
        if self.access_token:
            return self.access_token
        try:
            from azure.identity import DefaultAzureCredential
            return DefaultAzureCredential().get_token("https://management.azure.com/.default").token
        except Exception as exc:
            raise AzureDataFactoryError("Azure auth unavailable. Run az login or use managed identity.") from exc

    def list_pipeline_runs(self, days: int = 7, limit: int = 100):
        now = datetime.now(timezone.utc)
        url = ("https://management.azure.com/subscriptions/" + self.subscription_id +
            "/resourceGroups/" + self.resource_group +
            "/providers/Microsoft.DataFactory/factories/" + self.factory_name + "/queryPipelineRuns")
        body = {"lastUpdatedAfter": (now-timedelta(days=max(1,days))).isoformat(),
                "lastUpdatedBefore": now.isoformat(), "filters": [],
                "orderBy": [{"orderBy":"RunStart","order":"DESC"}]}
        try:
            response = requests.post(url, params={"api-version":self.api_version},
                headers={"Authorization":f"Bearer {self._get_token()}","Content-Type":"application/json"},
                json=body, timeout=self.timeout)
        except requests.RequestException as exc:
            raise AzureDataFactoryError(f"Azure Data Factory connection failed: {exc}") from exc
        if not response.ok:
            raise AzureDataFactoryError(f"Azure Data Factory API returned HTTP {response.status_code}: {response.text[:600]}")
        result=[]
        for item in response.json().get("value",[])[:limit]:
            status=item.get("status","Unknown")
            result.append({"run_id":item.get("runId",""),"job_id":None,
                "pipeline":item.get("pipelineName","Azure Data Factory pipeline"),
                "status":"Failed" if status in {"Failed","Cancelled"} else status,
                "duration_minutes":max(0,int(item.get("durationInMs",0)/60000)),
                "started_at":item.get("runStart",""),"error":item.get("message","") if status=="Failed" else "",
                "retry_count":0,"source":"Azure Data Factory","raw_lifecycle_state":status,"raw_result_state":status})
        return result
