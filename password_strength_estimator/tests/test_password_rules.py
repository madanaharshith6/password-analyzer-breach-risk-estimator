"""
Unit Tests for Rule-Based Evaluation Engine
Tests edge cases, structural heuristics, sequential detections, and scoring limits.
"""

import pytest
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from modules.password_rules import PasswordRuleEngine


@pytest.fixture
def rule_engine():
    return PasswordRuleEngine()


def test_empty_password(rule_engine):
    """Test empty password returns score 0 and Very Weak category."""
    res = rule_engine.evaluate("")
    assert res["score"] == 0.0
    assert res["category"] == "Very Weak"
    assert "Password is empty" in res["rules_failed"]


def test_short_password(rule_engine):
    """Test short passwords (<8 chars) trigger penalty and fail length check."""
    res = rule_engine.evaluate("Ab1!")
    assert res["length"] == 4
    assert res["score"] < 40.0
    assert any("Inadequate length" in f for f in res["rules_failed"])


def test_numeric_only_password(rule_engine):
    """Test digits-only passwords."""
    res = rule_engine.evaluate("1234567890")
    assert res["digits_count"] == 10
    assert res["uppercase_count"] == 0
    assert res["lowercase_count"] == 0
    assert res["special_count"] == 0
    assert res["has_numerical_sequence"] is True
    assert res["score"] < 45.0


def test_lowercase_only_password(rule_engine):
    """Test lowercase-only passwords."""
    res = rule_engine.evaluate("abcdefghijkl")
    assert res["lowercase_count"] == 12
    assert res["variety_count"] == 1
    assert res["has_alphabetical_sequence"] is True
    assert res["category"] in ["Very Weak", "Weak"]


def test_repeated_characters(rule_engine):
    """Test consecutive identical characters are penalized."""
    res = rule_engine.evaluate("aaaaaabbbbbb")
    assert res["max_consecutive_repeated"] >= 6
    assert any("repeated" in p.lower() for p in res["penalties"])


def test_keyboard_walk_sequence(rule_engine):
    """Test spatial keyboard walk sequences are caught."""
    res = rule_engine.evaluate("qwertyuiop")
    assert res["has_keyboard_sequence"] is True
    assert any("keyboard" in p.lower() for p in res["penalties"])


def test_dictionary_word_detection(rule_engine):
    """Test common password roots are detected."""
    res = rule_engine.evaluate("adminpassword123")
    assert "admin" in res["dictionary_matches"] or "password" in res["dictionary_matches"]
    assert any("dictionary" in p.lower() for p in res["penalties"])


def test_calendar_year_detection(rule_engine):
    """Test calendar year patterns (1900-2035) are penalized."""
    res = rule_engine.evaluate("Sunshine2024")
    assert res["has_year_pattern"] is True
    assert any("calendar year" in p.lower() for p in res["penalties"])


def test_strong_random_password(rule_engine):
    """Test high entropy, 16+ char random password achieves Very Strong."""
    res = rule_engine.evaluate("Kx9#mP2$vL8@qW4%zR")
    assert res["length"] >= 16
    assert res["variety_count"] == 4
    assert res["has_alphabetical_sequence"] is False
    assert res["has_numerical_sequence"] is False
    assert res["has_keyboard_sequence"] is False
    assert res["score"] >= 85.0
    assert res["category"] == "Very Strong"
