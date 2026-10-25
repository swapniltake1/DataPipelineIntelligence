# Self-Healing Data Pipeline Agent

A Python project for investigating failed data pipeline runs and deciding what to do next. The first version uses sample run data and simple rules to identify common problems, such as schema changes, failed data-quality checks, and timeouts.

The goal is to build this into a tool that can monitor Azure Data Factory and Databricks jobs, explain failures, and help an operator recover a pipeline safely.

## What works now

- Streamlit dashboard showing sample successful, failed, and delayed runs
- Basic failure classification and troubleshooting suggestions
- Approval check before a retry can be recorded
- Local JSONL audit log for operator decisions
- Unit tests for diagnosis and retry rules

The current version uses synthetic data. It does not connect to Azure or restart real jobs. Diagnosis is rule-based; LangGraph and Azure integrations are planned work.

## Run locally

Requires Python 3.10 or newer.

On Windows PowerShell, open this folder and run:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

If PowerShell prevents virtual-environment activation, run this in the same terminal and try again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

## Try it out

1. Open the Streamlit page in your browser.
2. Select a pipeline run from the list.
3. Read the error details and suggested next step.
4. Enter an operator name and review the retry option.
5. Record the decision and check the audit history.

Only transient failures are considered retry candidates, and the retry is simulated. Schema and data-quality failures need investigation before a rerun.

## Project layout

```text
app.py                  Streamlit dashboard
src/diagnosis.py        Failure classification rules
src/recovery.py         Retry policy and simulated action
src/audit.py            Local audit logging
data/sample_runs.json   Example pipeline runs
tests/test_diagnosis.py Unit tests
```

## Run the tests

```powershell
python -m pytest
```

## Planned work

- Use LangGraph to coordinate log parsing, diagnosis, policy checks, and recovery recommendations.
- Read pipeline run status from Azure Data Factory.
- Collect Databricks job status and relevant error details.
- Add PySpark checks for schema drift and data quality.
- Add authentication, role-based approvals, retry limits, and safeguards before any real recovery action.

## Configuration and security

An example environment file is included for future Azure settings. Do not commit credentials, access tokens, connection strings, or production logs. Any real retry integration should use least-privilege access, verify that a rerun is safe, and retain an audit trail.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
