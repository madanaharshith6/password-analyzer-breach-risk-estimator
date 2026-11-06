"""
Unit Tests for Feature Extraction Module
Tests 20-dimensional feature extraction, column alignment, and mathematical bounds.
"""

import pytest
import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from modules.feature_extraction import FeatureExtractor
from config import FEATURE_COLUMNS


@pytest.fixture
def extractor():
    return FeatureExtractor()


def test_feature_columns_count(extractor):
    """Ensure exactly 20 features are extracted and names match config."""
    feat_dict = extractor.extract_dict("TestP@ssw0rd123!")
    assert len(feat_dict) == 20
    assert list(feat_dict.keys()) == FEATURE_COLUMNS


def test_empty_password_features(extractor):
    """Ensure empty password yields all zeros without exceptions."""
    feat_dict = extractor.extract_dict("")
    assert feat_dict["length"] == 0.0
    assert feat_dict["shannon_entropy"] == 0.0
    assert feat_dict["char_variety"] == 0.0


def test_dataframe_shape(extractor):
    """Ensure DataFrame output matches expected dimensions (1, 20)."""
    df = extractor.extract_dataframe("SamplePassword#2024")
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (1, 20)
    assert list(df.columns) == FEATURE_COLUMNS


def test_batch_extraction(extractor):
    """Ensure batch extraction works for multiple passwords."""
    passwords = ["123456", "dragon", "Tr0ub4dor&3", "correct-horse-battery-staple-99!"]
    df_batch = extractor.extract_batch(passwords)
    assert len(df_batch) == 4
    assert df_batch.shape == (4, 20)


def test_entropy_bounds(extractor):
    """Test Shannon entropy values remain mathematically sound."""
    # Low entropy (all identical)
    f_low = extractor.extract_dict("aaaaaaaaaaaa")
    assert f_low["shannon_entropy"] == 0.0

    # High entropy (all unique symbols)
    f_high = extractor.extract_dict("abcdefghijkl")
    assert f_high["shannon_entropy"] > 3.0
