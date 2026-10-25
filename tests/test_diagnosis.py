from src.diagnosis import diagnose
from src.recovery import check_retry_policy


def test_schema_mismatch_is_not_retry_eligible():
    result = diagnose("Schema mismatch: incompatible schema", "Failed")
    assert result.category == "Schema mismatch"
    assert result.retry_eligible is False


def test_timeout_can_be_retry_eligible():
    result = diagnose("Request timed out", "Failed")
    assert result.category == "Transient / timeout"
    assert result.retry_eligible is True


def test_retry_requires_approval():
    decision = check_retry_policy(True, False, 0)
    assert decision.allowed is False


def test_retry_limit_is_enforced():
    decision = check_retry_policy(True, True, 2, max_retries=2)
    assert decision.allowed is False
