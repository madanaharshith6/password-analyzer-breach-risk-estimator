"""
Integration Tests for Hybrid Prediction Engine
Tests fusion logic, cybersecurity override safeguards, and end-to-end evaluation.
"""

import pytest
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from modules.hybrid_engine import HybridStrengthEngine


@pytest.fixture
def engine():
    return HybridStrengthEngine()


def test_empty_password_hybrid(engine):
    """Ensure empty password returns 0.0 hybrid score."""
    res = engine.analyze("")
    assert res["hybrid_score"] == 0.0
    assert res["hybrid_category"] == "Very Weak"


def test_compromised_password_safeguard_override(engine):
    """
    CRITICAL TEST:
    A known compromised password (e.g. 'password', '123456', or 'p@ssw0rd')
    MUST be clamped to Very Weak regardless of character variety or length!
    """
    res = engine.analyze("password")
    assert res["safeguard_override"] is True
    assert res["hybrid_category"] == "Very Weak"
    assert res["hybrid_score"] <= 20.0


def test_long_strong_passphrase(engine):
    """Ensure a long random passphrase receives Strong or Very Strong rating."""
    res = engine.analyze("Quantum#Horizon-Glacier*Velocity89!")
    assert res["password_length"] >= 20
    assert res["hybrid_category"] in ["Strong", "Very Strong"]
    assert res["hybrid_score"] >= 75.0
    assert res["safeguard_override"] is False


def test_recommendations_populated(engine):
    """Ensure recommendations list is generated for weak passwords."""
    res = engine.analyze("abc123")
    assert len(res["recommendations"]) > 0
    priorities = [r["priority"] for r in res["recommendations"]]
    assert "CRITICAL" in priorities or "HIGH" in priorities
