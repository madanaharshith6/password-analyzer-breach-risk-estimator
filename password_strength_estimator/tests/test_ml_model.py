"""
Unit Tests for Machine Learning Model Wrapper
Tests inference, scaling, probabilities, and champion model compatibility.
"""

import pytest
import sys
from pathlib import Path
import pandas as pd

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from modules.ml_model import MLPasswordModel
from modules.feature_extraction import FeatureExtractor
from config import MODEL_FILE, STRENGTH_LABELS


@pytest.fixture
def ml_model():
    return MLPasswordModel()


@pytest.fixture
def extractor():
    return FeatureExtractor()


def test_model_is_loaded(ml_model):
    """Ensure trained model artifact exists and was loaded cleanly."""
    assert ml_model.is_loaded is True
    assert ml_model.model is not None
    assert ml_model.scaler is not None


def test_predict_weak_password(ml_model, extractor):
    """Ensure a short simple password is classified as Very Weak or Weak."""
    feat_df = extractor.extract_dataframe("123456")
    pred = ml_model.predict(feat_df)
    assert pred["model_available"] is True
    assert pred["predicted_class"] in [0, 1]
    assert pred["predicted_label"] in ["Very Weak", "Weak"]


def test_predict_strong_password(ml_model, extractor):
    """Ensure high entropy password is classified as Strong or Very Strong."""
    feat_df = extractor.extract_dataframe("Kx9#mP2$vL8@qW4%zR6&hT")
    pred = ml_model.predict(feat_df)
    assert pred["predicted_class"] in [3, 4]
    assert pred["predicted_label"] in ["Strong", "Very Strong"]


def test_probabilities_sum_to_one(ml_model, extractor):
    """Ensure prediction probabilities sum approximately to 1.0."""
    feat_df = extractor.extract_dataframe("ModerateP@ss99")
    pred = ml_model.predict(feat_df)
    probs = pred["probabilities"]
    total = sum(probs.values())
    assert abs(total - 1.0) < 0.05
