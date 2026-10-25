"""Safety policy and simulated retry action. No Azure calls are made."""
from dataclasses import dataclass


@dataclass(frozen=True)
class RecoveryDecision:
    allowed: bool
    message: str


def check_retry_policy(
    retry_eligible: bool,
    approved: bool,
    previous_retry_count: int,
    max_retries: int = 2,
) -> RecoveryDecision:
    if not retry_eligible:
        return RecoveryDecision(False, "This failure category is not eligible for automatic retry.")
    if not approved:
        return RecoveryDecision(False, "Operator approval is required before retry.")
    if previous_retry_count >= max_retries:
        return RecoveryDecision(False, f"Retry limit reached ({max_retries}).")
    return RecoveryDecision(True, "Policy checks passed. Demo retry can be recorded.")


def simulate_retry(run_id: str) -> str:
    """Return a simulation message; deliberately does not invoke external systems."""
    return f"SIMULATED ONLY: retry request prepared for {run_id}. No real job was restarted."
