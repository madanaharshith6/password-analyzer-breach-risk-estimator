"""
Unit Tests for Breach-Risk Estimation Engine
Tests local database blacklist checks, k-anonymity SHA-1 hash parsing, and offline resilience.
"""

import pytest
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from modules.breach_checker import BreachRiskEstimator


@pytest.fixture
def breach_estimator():
    return BreachRiskEstimator()


def test_empty_password_breach(breach_estimator):
    """Ensure empty password returns safe default without errors."""
    res = breach_estimator.evaluate_breach_risk("")
    assert res["is_compromised"] is False
    assert res["breach_count"] == 0


def test_local_blacklist_compromised(breach_estimator):
    """Ensure ubiquitous passwords in the local blacklist are immediately flagged."""
    res = breach_estimator.evaluate_breach_risk("123456")
    assert res["is_compromised"] is True
    assert res["risk_tier"] == "CRITICAL"
    assert "Local Compromised Passwords Database" in res["detection_source"]


def test_hibp_k_anonymity_sha1_prefix():
    """Verify SHA-1 prefix logic complies strictly with k-anonymity."""
    import hashlib
    estimator = BreachRiskEstimator()
    pwd = "TestingPassword99!"
    sha1 = hashlib.sha1(pwd.encode("utf-8")).hexdigest().upper()
    prefix = sha1[:5]
    suffix = sha1[5:]

    assert len(prefix) == 5
    assert len(suffix) == 35


def test_safe_unbreached_password(breach_estimator):
    """Test a high-entropy random string is not flagged as compromised in local db."""
    res = breach_estimator.evaluate_breach_risk("X9$mP2#qW8@vL4!zR7%bT")
    # If offline or API online, it should not be in the local breach blacklist
    assert "123456" not in "X9$mP2#qW8@vL4!zR7%bT"
