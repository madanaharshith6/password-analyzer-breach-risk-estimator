"""
Unit and Integration Tests for Security Insights Calculations and Privacy-Preserving Audit Database
Student: MADANA KOMAL SIVA SAI HARSHITH (Roll No: 24ME5A5408)
"""

import math
import importlib.util
from pathlib import Path
import pytest
from database.history import AuditHistoryManager
from database.db import PasswordAnalysisRecord, get_session

# Dynamically import 3_Security_Insights.py due to leading digit in filename
BASE_DIR = Path(__file__).resolve().parent.parent
insights_path = BASE_DIR / "pages" / "3_Security_Insights.py"
spec = importlib.util.spec_from_file_location("security_insights", insights_path)
security_insights = importlib.util.module_from_spec(spec)
spec.loader.exec_module(security_insights)

format_crack_duration = security_insights.format_crack_duration
PASSPHRASE_WORDLIST = security_insights.PASSPHRASE_WORDLIST


def test_format_crack_duration_never_rounds_to_zero_million_years():
    """Verify that intermediate durations between 1,000 and 1,000,000 years format cleanly as thousand years."""
    # 1,500 years in seconds
    sec_1500_years = 1500 * 31536000
    formatted = format_crack_duration(sec_1500_years)
    assert "0.0" not in formatted
    assert "thousand years" in formatted
    assert formatted == "1.5 thousand years"


def test_format_crack_duration_ranges():
    """Verify scaling across ms, seconds, minutes, hours, days, years, millions, billions."""
    assert "millisecond" in format_crack_duration(0.005)
    assert "seconds" in format_crack_duration(12.5)
    assert "minutes" in format_crack_duration(180)
    assert "hours" in format_crack_duration(7200)
    assert "days" in format_crack_duration(172800)
    assert "years" in format_crack_duration(31536000 * 10)
    assert "million years" in format_crack_duration(31536000 * 5000000)
    assert "billion years" in format_crack_duration(31536000 * 4000000000)


def test_passphrase_wordlist_integrity():
    """Verify passphrase wordlist has exactly 256 unique, non-empty, lowercase words."""
    assert len(PASSPHRASE_WORDLIST) == 256
    assert len(set(PASSPHRASE_WORDLIST)) == 256
    for word in PASSPHRASE_WORDLIST:
        assert word.isalpha()
        assert word.islower()
        assert len(word) >= 3


def test_passphrase_theoretical_entropy():
    """Verify that 4 words selected from 256 words yield exactly 32 bits of word choice entropy."""
    wordlist_size = len(PASSPHRASE_WORDLIST)
    entropy_per_word = math.log2(wordlist_size)
    assert entropy_per_word == 8.0  # log2(256) = 8.0
    four_word_entropy = 4 * entropy_per_word
    assert four_word_entropy == 32.0


def test_audit_database_no_passwords_or_hashes_stored():
    """Verify that AuditHistoryManager persists only telemetry metadata and never stores passwords or hashes."""
    mgr = AuditHistoryManager()
    analysis_id = mgr.record_analysis(
        strength_category="Strong",
        rule_score=82.5,
        ml_prediction="Strong",
        breach_risk_category="LOW",
        entropy_score=64.2,
        password_length=14
    )
    assert analysis_id is not None

    session = get_session()
    try:
        record = session.query(PasswordAnalysisRecord).filter_by(analysis_id=analysis_id).first()
        assert record is not None
        assert record.strength_category == "Strong"
        assert record.rule_score == 82.5
        assert record.ml_prediction == "Strong"
        assert record.breach_risk_category == "LOW"
        assert record.entropy_score == 64.2
        assert record.length_bucket == "12-15 chars"
        
        # Verify that record object has NO password or hash attributes
        assert not hasattr(record, "password")
        assert not hasattr(record, "plaintext")
        assert not hasattr(record, "hash")
        assert not hasattr(record, "sha1")
        assert not hasattr(record, "sha256")
    finally:
        session.close()
