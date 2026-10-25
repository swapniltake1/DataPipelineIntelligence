"""Connected monitoring dashboard. Set APP_MODE in .env and restart."""
import json
from pathlib import Path
import pandas as pd
import streamlit as st
from src.config import get_settings
from src.databricks_client import DatabricksClient
from src.azure_data_factory import AzureDataFactoryClient
from src.agent import run_diagnosis
from src.audit import record_event

st.set_page_config(page_title="DataPipelineIntelligence", layout="wide")
cfg = get_settings()
st.title("DataPipelineIntelligence")
st.caption("Read-only live monitoring plus diagnosis and audit.")
if cfg.app_mode == "demo":
    runs = json.loads(Path("data/sample_runs.json").read_text(encoding="utf-8"))
    for r in runs:
        r.setdefault("source", "Sample data")
    st.info("Demo mode uses synthetic sample runs.")
else:
    if not cfg.databricks_configured:
        st.error("Set the matching workspace host and token in .env, then restart.")
        st.stop()
    try:
        runs = DatabricksClient(cfg.databricks_host, cfg.databricks_token, cfg.request_timeout_seconds).list_runs()
        if cfg.app_mode == "azure" and cfg.adf_configured:
            runs += AzureDataFactoryClient(cfg.azure_subscription_id, cfg.azure_resource_group,
                cfg.azure_data_factory_name, cfg.azure_access_token,
                cfg.azure_management_api_version, cfg.request_timeout_seconds).list_pipeline_runs()
        st.success("Connected to configured workspace.")
    except Exception as exc:
        st.error(str(exc))
        st.stop()
if not runs:
    st.info("No runs returned.")
    st.stop()
df = pd.DataFrame(runs)
a,b,c = st.columns(3)
a.metric("Runs",len(runs))
b.metric("Failed",sum(str(x.get("status","")).lower()=="failed" for x in runs))
c.metric("Succeeded",sum(str(x.get("status","")).lower()=="succeeded" for x in runs))
st.dataframe(df, use_container_width=True, hide_index=True)
i = st.selectbox("Run to diagnose",range(len(runs)),format_func=lambda n:f"{runs[n].get('source','')} · {runs[n].get('pipeline','')} · {runs[n].get('status','')}")
run = runs[i]
d = run_diagnosis(run.get("error",""),run.get("status","Failed"))
st.subheader("Diagnosis")
st.write("**Category:**",d.category)
st.write("**Likely cause:**",d.likely_cause)
st.write("**Recommendation:**",d.recommendation)
st.warning("Live recovery is disabled. This app records decisions only.")
operator = st.text_input("Operator name")
approved = st.checkbox("I reviewed the diagnosis")
if st.button("Record review"):
    if not operator.strip():
        st.error("Enter an operator name.")
    else:
        record_event({"run_id":str(run.get("run_id","")),"pipeline":run.get("pipeline",""),
            "source":run.get("source",""),"operator":operator.strip(),"approved":approved,
            "diagnosis_category":d.category,"action":"review_only","result":"No live recovery action executed."})
        st.success("Review recorded.")
