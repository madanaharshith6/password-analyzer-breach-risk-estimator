"""
Adversarial & Generalization Security Audit Tests
Specifically targets shortcut learning vulnerabilities, out-of-distribution patterns,
and conservative hybrid override bounds.
"""

import pytest
import sys
from pathlib import Path
import pandas as pd

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from modules.hybrid_engine import HybridStrengthEngine
from modules.password_rules import PasswordRuleEngine
from modules.ml_model import MLPasswordModel
from modules.feature_extraction import FeatureExtractor
from config import DATASET_DIR


@pytest.fixture
def hybrid_engine():
    return HybridStrengthEngine()


@pytest.fixture
def rule_engine():
    return PasswordRuleEngine()


@pytest.fixture
def ml_model():
    return MLPasswordModel()


@pytest.fixture
def extractor():
    return FeatureExtractor()


def test_adversarial_long_repeated_characters(hybrid_engine, rule_engine):
    """
    AUDIT TEST 1:
    A password of 18 identical characters ('aaaaaaaaaaaaaaaaaa') must NOT receive
    a Strong rating simply because length >= 16. It must be evaluated as Very Weak.
    """
    pwd = "aaaaaaaaaaaaaaaaaa"
    r_res = rule_engine.evaluate(pwd)
    h_res = hybrid_engine.analyze(pwd)

    assert r_res["score"] < 25.0
    assert r_res["category"] == "Very Weak"
    assert h_res["hybrid_category"] == "Very Weak"
    assert h_res["hybrid_score"] < 25.0
    assert h_res["safeguard_override"] is True


def test_adversarial_long_numerical_sequence(hybrid_engine, rule_engine):
    """
    AUDIT TEST 2:
    A password of 20 sequential digits ('12345678901234567890') must NOT receive
    a Strong rating. It must be evaluated as Very Weak.
    """
    pwd = "12345678901234567890"
    r_res = rule_engine.evaluate(pwd)
    h_res = hybrid_engine.analyze(pwd)

    assert r_res["has_numerical_sequence"] is True
    assert r_res["category"] == "Very Weak"
    assert h_res["hybrid_category"] == "Very Weak"
    assert h_res["hybrid_score"] < 25.0


def test_adversarial_long_repeated_dictionary_words(hybrid_engine):
    """
    AUDIT TEST 3:
    Repeating a dictionary word ('passwordpasswordpassword', 24 chars)
    must NOT fool the system into a Strong classification.
    """
    pwd = "passwordpasswordpassword"
    h_res = hybrid_engine.analyze(pwd)

    assert h_res["hybrid_category"] == "Very Weak"
    assert h_res["hybrid_score"] <= 20.0


def test_adversarial_long_keyboard_walk(hybrid_engine, rule_engine):
    """
    AUDIT TEST 4:
    A 26-character full keyboard row walk ('qwertyuiopasdfghjklzxcvbnm')
    must be classified as Very Weak.
    """
    pwd = "qwertyuiopasdfghjklzxcvbnm"
    r_res = rule_engine.evaluate(pwd)
    h_res = hybrid_engine.analyze(pwd)

    assert r_res["has_keyboard_sequence"] is True
    assert r_res["category"] == "Very Weak"
    assert h_res["hybrid_category"] == "Very Weak"


def test_short_password_with_four_character_types(hybrid_engine):
    """
    AUDIT TEST 5:
    A 6-character password with all 4 character types ('Ab1!@#') has low search space
    (crackable in seconds) and must NEVER receive a Strong rating.
    """
    pwd = "Ab1!@#"
    h_res = hybrid_engine.analyze(pwd)

    assert h_res["password_length"] == 6
    assert h_res["hybrid_category"] in ["Very Weak", "Weak"]
    assert h_res["hybrid_score"] <= 40.0


def test_challenging_holdout_dataset_integrity():
    """
    AUDIT TEST 6:
    Verify the independent Challenging Adversarial Holdout Dataset exists,
    contains exactly 250 samples, and is balanced across all 5 classes.
    """
    holdout_path = DATASET_DIR / "challenging_holdout.csv"
    assert holdout_path.exists()
    df = pd.read_csv(holdout_path)
    assert len(df) == 250
    counts = df["ground_truth_label"].value_counts().to_dict()
    for cls_idx in range(5):
        assert counts.get(cls_idx, 0) == 50


def test_effective_entropy_calculation(rule_engine):
    """
    AUDIT TEST 7:
    Ensure effective brute-force search space entropy collapses for monotonic passwords.
    """
    ent_monotonic = rule_engine.calculate_entropy_bits("aaaaaaaaaaaaaaaaaa")
    ent_random = rule_engine.calculate_entropy_bits("Kx9#mP2$vL8@qW4%zR")

    assert ent_monotonic < 10.0  # Should be ~4.7 bits (log2(26))
    assert ent_random > 70.0     # Genuine high entropy
