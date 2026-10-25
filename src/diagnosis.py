"""Deterministic starter diagnostics for common pipeline failures."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Diagnosis:
    category: str
    likely_cause: str
    recommendation: str
    retry_eligible: bool
    confidence: str


RULES = [
    (
        ("schema", "column not found", "datatype mismatch", "incompatible schema"),
        Diagnosis(
            "Schema mismatch",
            "The incoming dataset may have added, removed, or changed a column or data type.",
            "Compare source and target schemas; confirm an approved schema evolution before rerunning.",
            False,
            "High",
        ),
    ),
    (
        ("null", "duplicate", "quality check", "constraint violation", "out of range"),
        Diagnosis(
            "Data-quality failure",
            "A validation rule detected missing, duplicate, or invalid records.",
            "Inspect rejected rows and validation metrics; fix or quarantine bad records before rerunning.",
            False,
            "High",
        ),
    ),
    (
        ("timeout", "timed out", "temporarily unavailable", "429", "throttl"),
        Diagnosis(
            "Transient / timeout",
            "The service may have been temporarily unavailable or throttled.",
            "Check service health and retry limits. A bounded retry may be appropriate after approval.",
            True,
            "Medium",
        ),
    ),
    (
        ("network", "connection reset", "temporary", "transient"),
        Diagnosis(
            "Transient connectivity",
            "A temporary network or dependency issue may have interrupted execution.",
            "Verify dependency health and use a bounded retry only if the operation is idempotent.",
            True,
            "Medium",
        ),
    ),
]


def diagnose(error_text: str, status: str = "Failed") -> Diagnosis:
    """Classify a failure using simple keyword rules; no external services are called."""
    text = (error_text or "").lower()
    for keywords, diagnosis in RULES:
        if any(keyword in text for keyword in keywords):
            return diagnosis
    if status.lower() in {"delayed", "running late"}:
        return Diagnosis(
            "Pipeline delay",
            "The run has exceeded its expected duration; the cause is not yet known.",
            "Check upstream dependencies, recent duration trends, and current compute capacity.",
            False,
            "Low",
        )
    return Diagnosis(
        "Unknown",
        "The available error details are insufficient to identify a reliable root cause.",
        "Collect sanitized logs and run metadata; escalate to the pipeline owner before recovery.",
        False,
        "Low",
    )
