"""
Feature Extraction Module for Password Machine Learning Model
Extracts numerical representations and pattern vectors without storing or transmitting raw passwords.
"""

import math
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Union
from config import FEATURE_COLUMNS, COMMON_DICTIONARY_WORDS, KEYBOARD_PATTERNS


class FeatureExtractor:
    """
    Transforms password strings into standardized 20-dimensional numerical feature vectors
    for machine learning training and inference.
    """

    def __init__(self):
        self.common_words = set(COMMON_DICTIONARY_WORDS)
        self.keyboard_patterns = [p.lower() for p in KEYBOARD_PATTERNS]

    def _calc_shannon_entropy(self, s: str) -> float:
        if not s:
            return 0.0
        length = len(s)
        freq = {}
        for c in s:
            freq[c] = freq.get(c, 0) + 1
        ent = 0.0
        for count in freq.values():
            p = count / length
            ent -= p * math.log2(p)
        return float(ent)

    def _calc_pool_size(self, s: str) -> int:
        pool = 0
        if any(c.islower() for c in s):
            pool += 26
        if any(c.isupper() for c in s):
            pool += 26
        if any(c.isdigit() for c in s):
            pool += 10
        if any(not c.isalnum() for c in s):
            pool += 33
        return max(pool, 1)

    def _max_consecutive_repeats(self, s: str) -> int:
        if not s:
            return 0
        max_run = 1
        curr = 1
        for i in range(1, len(s)):
            if s[i] == s[i - 1]:
                curr += 1
                max_run = max(max_run, curr)
            else:
                curr = 1
        return max_run

    def _has_seq_alpha(self, s: str, min_len: int = 3) -> int:
        lower = s.lower()
        if len(lower) < min_len:
            return 0
        for i in range(len(lower) - min_len + 1):
            sub = lower[i:i + min_len]
            if all(c.isalpha() for c in sub):
                diffs = [ord(sub[j+1]) - ord(sub[j]) for j in range(len(sub) - 1)]
                if all(d == 1 for d in diffs) or all(d == -1 for d in diffs):
                    return 1
        return 0

    def _has_seq_num(self, s: str, min_len: int = 3) -> int:
        if len(s) < min_len:
            return 0
        for i in range(len(s) - min_len + 1):
            sub = s[i:i + min_len]
            if sub.isdigit():
                diffs = [ord(sub[j+1]) - ord(sub[j]) for j in range(len(sub) - 1)]
                if all(d == 1 for d in diffs) or all(d == -1 for d in diffs):
                    return 1
        return 0

    def _has_keyboard_walk(self, s: str, min_len: int = 4) -> int:
        lower = s.lower()
        if len(lower) < min_len:
            return 0
        for row in self.keyboard_patterns:
            rev_row = row[::-1]
            for i in range(len(lower) - min_len + 1):
                sub = lower[i:i + min_len]
                if sub in row or sub in rev_row:
                    return 1
        return 0

    def _has_common_word(self, s: str) -> int:
        lower = s.lower()
        for w in self.common_words:
            if len(w) >= 4 and w in lower:
                return 1
        return 0

    def _has_year(self, s: str) -> int:
        import re
        return 1 if re.search(r"(19\d\d|20[0-3]\d)", s) else 0

    def extract_dict(self, password: str) -> Dict[str, float]:
        """Extract features as a dictionary mapped to FEATURE_COLUMNS."""
        if not password:
            return {col: 0.0 for col in FEATURE_COLUMNS}

        length = len(password)
        n_upper = sum(1 for c in password if c.isupper())
        n_lower = sum(1 for c in password if c.islower())
        n_digits = sum(1 for c in password if c.isdigit())
        n_special = sum(1 for c in password if not c.isalnum())

        variety = sum([n_lower > 0, n_upper > 0, n_digits > 0, n_special > 0])
        unique_ratio = len(set(password)) / length
        shannon = self._calc_shannon_entropy(password)
        pool = self._calc_pool_size(password)
        
        # Calculate realistic combinatorial search space entropy
        if len(set(password)) <= 2:
            entropy_bits = math.log2(pool)
        else:
            max_shannon = math.log2(pool) if pool > 1 else 1.0
            efficiency = min(1.0, max(0.1, shannon / max_shannon))
            entropy_bits = length * math.log2(pool) * efficiency

        return {
            "length": float(length),
            "num_uppercase": float(n_upper),
            "num_lowercase": float(n_lower),
            "num_digits": float(n_digits),
            "num_special": float(n_special),
            "ratio_uppercase": float(n_upper / length),
            "ratio_lowercase": float(n_lower / length),
            "ratio_digits": float(n_digits / length),
            "ratio_special": float(n_special / length),
            "char_variety": float(variety),
            "unique_char_ratio": float(unique_ratio),
            "shannon_entropy": float(round(shannon, 4)),
            "max_consecutive_repeated": float(self._max_consecutive_repeats(password)),
            "has_sequential_char": float(self._has_seq_alpha(password)),
            "has_sequential_num": float(self._has_seq_num(password)),
            "has_keyboard_seq": float(self._has_keyboard_walk(password)),
            "has_common_word": float(self._has_common_word(password)),
            "has_year_pattern": float(self._has_year(password)),
            "pool_size": float(pool),
            "entropy_bits": float(round(entropy_bits, 4))
        }

    def extract_dataframe(self, password: str) -> pd.DataFrame:
        """Extract features and return as a single-row Pandas DataFrame."""
        feat_dict = self.extract_dict(password)
        df = pd.DataFrame([feat_dict], columns=FEATURE_COLUMNS)
        return df

    def extract_batch(self, passwords: List[str]) -> pd.DataFrame:
        """Extract features for a list of passwords."""
        rows = [self.extract_dict(p) for p in passwords]
        return pd.DataFrame(rows, columns=FEATURE_COLUMNS)
