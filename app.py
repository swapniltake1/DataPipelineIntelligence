from datetime import datetime, timezone
import json
from pathlib import Path

import pandas as pd
import streamlit as st

from src.audit import record_event
from src.diagnosis import diagnose
from src.recovery import check_retry_policy, simulate_retry

st.set_page_config(page_title="Self-Healing Pipeline Agent", page_icon="🛠️", layout="wide")

DATA_PATH = Path("data/sample_runs.json")
with DATA_PATH.open("r", encoding="utf-8") as file:
    runs = json.load(file)

st.title("Self-Healing Data Pipeline Agent")
st.caption("Local MVP · synthetic run data · retry actions are simulated only")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Pipeline runs", len(runs))
m2.metric("Failed", sum(r["status"] == "Failed" for r in runs))
m3.metric("Delayed", sum(r["status"] == "Delayed" for r in runs))
m4.metric("Successful", sum(r["status"] == "Succeeded" for r in runs))

st.subheader("Pipeline run monitor")
df = pd.DataFrame(runs)
st.dataframe(df[["run_id", "pipeline", "status", "duration_minutes", "started_at"]], use_container_width=True, hide_index=True)

selected_id = st.selectbox("Select a run to investigate", [r["run_id"] for r in runs])
run = next(r for r in runs if r["run_id"] == selected_id)
diagnosis = diagnose(run.get("error", ""), run["status"])

left, right = st.columns([3, 2])
with left:
    st.subheader("Run details")
    st.write(f"**Pipeline:** {run['pipeline']}")
    st.write(f"**Status:** {run['status']}")
    st.write(f"**Error details:** {run.get('error') or 'No error reported.'}")
    st.subheader("Diagnosis")
    st.write(f"**Category:** {diagnosis.category}")
    st.write(f"**Likely cause:** {diagnosis.likely_cause}")
    st.write(f"**Recommendation:** {diagnosis.recommendation}")
    st.caption(f"Rule-based confidence: {diagnosis.confidence}")

with right:
    st.subheader("Recovery approval")
    st.warning("This MVP never restarts a real Azure pipeline.")
    operator = st.text_input("Operator name", placeholder="Enter your name")
    approved = st.checkbox("I reviewed the recommendation and approve a simulated retry")
    previous_retry_count = int(run.get("retry_count", 0))
    decision = check_retry_policy(
        retry_eligible=diagnosis.retry_eligible,
        approved=approved,
        previous_retry_count=previous_retry_count,
    )
    st.write(f"**Retry eligible:** {'Yes' if diagnosis.retry_eligible else 'No'}")
    st.write(f"**Policy:** {decision.message}")

    if st.button("Record recovery decision", type="primary", use_container_width=True):
        if not operator.strip():
            st.error("Enter an operator name before recording a decision.")
        else:
            event = {
                "run_id": run["run_id"],
                "pipeline": run["pipeline"],
                "operator": operator.strip(),
                "approved": bool(approved),
                "retry_eligible": diagnosis.retry_eligible,
                "policy_allowed": decision.allowed,
                "diagnosis_category": diagnosis.category,
                "action": "simulated_retry" if decision.allowed else "no_retry",
                "result": simulate_retry(run["run_id"]) if decision.allowed else decision.message,
            }
            record_event(event)
            if decision.allowed:
                st.success(event["result"])
            else:
                st.info(f"Decision recorded. {decision.message}")

st.subheader("Audit history")
audit_path = Path("logs/audit.jsonl")
if audit_path.exists():
    events = []
    for line in audit_path.read_text(encoding="utf-8").splitlines():
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    if events:
        st.dataframe(pd.DataFrame(events[::-1]), use_container_width=True, hide_index=True)
    else:
        st.info("Audit log is empty.")
else:
    st.info("No decisions recorded yet. Decisions will appear here.")
