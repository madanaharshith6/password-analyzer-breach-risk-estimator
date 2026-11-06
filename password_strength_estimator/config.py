"""
Project Configuration and Global Constants
Password Strength and Breach-Risk Estimator
"""

import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
MODULES_DIR = BASE_DIR / "modules"
ML_DIR = BASE_DIR / "machine_learning"
DATASET_DIR = ML_DIR / "dataset"
SAVED_MODEL_DIR = ML_DIR / "saved_model"
DATABASE_DIR = BASE_DIR / "database"
ASSETS_DIR = BASE_DIR / "assets"

# Database Configuration
DATABASE_PATH = DATABASE_DIR / "password_audit.db"
DATABASE_URI = f"sqlite:///{DATABASE_PATH}"

# Model Configuration
MODEL_FILE = SAVED_MODEL_DIR / "best_model.joblib"
METRICS_FILE = SAVED_MODEL_DIR / "model_metrics.json"

# Categorization and Classes (5-Tier Scheme)
STRENGTH_LABELS = {
    0: "Very Weak",
    1: "Weak",
    2: "Moderate",
    3: "Strong",
    4: "Very Strong"
}

STRENGTH_COLORS = {
    "Very Weak": "#FF4B4B",     # Crimson / Red
    "Weak": "#FFA726",          # Orange
    "Moderate": "#FFEE58",      # Amber / Yellow
    "Strong": "#66BB6A",        # Light Green
    "Very Strong": "#2E7D32"    # Emerald Green
}

# Breach Risk Tiers
BREACH_RISK_LEVELS = {
    "CRITICAL": {"label": "Critical Breach Risk", "color": "#D32F2F"},
    "HIGH": {"label": "High Risk (Pattern/Dictionary Match)", "color": "#F57C00"},
    "MODERATE": {"label": "Moderate Risk", "color": "#FBC02D"},
    "LOW": {"label": "Low Risk", "color": "#388E3C"}
}

# Numerical Feature Columns (20 Engineered Features for ML)
FEATURE_COLUMNS = [
    "length",
    "num_uppercase",
    "num_lowercase",
    "num_digits",
    "num_special",
    "ratio_uppercase",
    "ratio_lowercase",
    "ratio_digits",
    "ratio_special",
    "char_variety",
    "unique_char_ratio",
    "shannon_entropy",
    "max_consecutive_repeated",
    "has_sequential_char",
    "has_sequential_num",
    "has_keyboard_seq",
    "has_common_word",
    "has_year_pattern",
    "pool_size",
    "entropy_bits"
]

# Common Password Substrings and Dictionary Roots
COMMON_DICTIONARY_WORDS = [
    "password", "admin", "welcome", "login", "master", "monkey", "dragon",
    "qwerty", "letmein", "football", "baseball", "iloveyou", "trustno1",
    "princess", "solo", "jordan", "shadow", "superman", "batman", "secret",
    "access", "default", "system", "passcode", "starwars", "chelsea",
    "liverpool", "barcelona", "arsenal", "computer", "internet", "security",
    "hunter", "testing", "sample", "server", "service", "summer", "winter",
    "spring", "autumn", "freedom", "matrix", "pokemon", "monster", "family"
]

# Keyboard Sequences for sequence detection
KEYBOARD_PATTERNS = [
    "qwertyuiop", "asdfghjkl", "zxcvbnm",
    "1234567890", "0987654321",
    "poiuytrewq", "lkjhgfdsa", "mnbvcxz",
    "!@#$%^&*()"
]

# Have I Been Pwned API Endpoint
HIBP_API_URL = "https://api.pwnedpasswords.com/range/"
HIBP_REQUEST_TIMEOUT = 3.5  # seconds
