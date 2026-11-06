"""
Dataset Generation and Preprocessing Module
Synthesizes a balanced, empirical password security corpus, extracts 20 numerical features,
and performs stratified train-test splitting with zero data leakage.
"""

import os
import sys
from pathlib import Path
import json
import random
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from config import DATASET_DIR, SAVED_MODEL_DIR, FEATURE_COLUMNS, STRENGTH_LABELS, ASSETS_DIR
from modules.feature_extraction import FeatureExtractor

# Set matplotlib cache directory to avoid permissions issues
os.environ["MPLCONFIGDIR"] = str(ASSETS_DIR / "mpl_cache")
(ASSETS_DIR / "mpl_cache").mkdir(parents=True, exist_ok=True)


def generate_empirical_dataset(samples_per_class: int = 1000, random_seed: int = 42) -> pd.DataFrame:
    """
    Constructs an empirical, balanced password dataset across 5 ground-truth strength classes:
    0: Very Weak, 1: Weak, 2: Moderate, 3: Strong, 4: Very Strong.
    """
    random.seed(random_seed)
    np.random.seed(random_seed)

    data = []

    # -------------------------------------------------------------
    # Class 0: Very Weak (Single type, repetitive, sequential, keyboard walks across ALL lengths)
    # -------------------------------------------------------------
    c0_roots = [
        "123456", "password", "12345678", "qwerty", "12345", "123456789", "football",
        "1234", "111111", "admin", "welcome", "login", "master", "monkey", "dragon",
        "letmein", "princess", "solo", "jordan", "shadow", "superman", "batman",
        "secret", "pass123", "testing", "server", "system", "summer", "winter",
        "spring", "autumn", "freedom", "matrix", "pokemon", "monster", "family",
        "abc", "123", "0000", "aaaa", "test", "demo", "guest", "root", "user"
    ]
    for _ in range(samples_per_class):
        mode = random.randint(1, 9)
        if mode == 1:
            pwd = random.choice(c0_roots)
        elif mode == 2:
            # Short numbers or letters (3-6)
            length = random.randint(3, 6)
            pwd = "".join(random.choices("0123456789", k=length))
        elif mode == 3:
            # Single character repetition short (4-7)
            char = random.choice("abcdefghijklmnopqrstuvwxyz1234567890")
            pwd = char * random.randint(4, 7)
        elif mode == 4:
            # Short keyboard walks
            walks = ["qwer", "asdf", "zxcv", "1234", "qwerty", "asdfgh", "zxcvbn"]
            pwd = random.choice(walks)
        elif mode == 5:
            # Short all-lowercase
            length = random.randint(4, 6)
            pwd = "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=length))
        elif mode == 6:
            # Adversarial: LONG repeated character runs (14-28 chars, e.g. 'aaaaaaaaaaaaaaaaaa')
            char = random.choice("abcdefghijklmnopqrstuvwxyz1234567890!@#$")
            pwd = char * random.randint(14, 28)
        elif mode == 7:
            # Adversarial: LONG sequential numbers (12-24 chars, e.g. '12345678901234567890')
            base_seq = "0123456789" * 4
            start = random.randint(0, 10)
            k_len = random.randint(12, 24)
            pwd = base_seq[start:start + k_len]
        elif mode == 8:
            # Adversarial: LONG keyboard walks (16-30 chars, e.g. 'qwertyuiopasdfghjklzxcvbnm')
            kb_full = "qwertyuiopasdfghjklzxcvbnm1234567890" * 2
            start = random.randint(0, 10)
            k_len = random.randint(16, 28)
            pwd = kb_full[start:start + k_len]
        else:
            # Adversarial: LONG repeated dictionary words (16-32 chars, e.g. 'passwordpasswordpassword')
            word = random.choice(["password", "admin", "welcome", "monkey", "dragon", "testing"])
            repeats = random.randint(2, 4)
            pwd = word * repeats
        data.append({"password": pwd, "label": 0})

    # -------------------------------------------------------------
    # Class 1: Weak (Predictable structures, names with years, long all-lowercase phrases)
    # -------------------------------------------------------------
    c1_words = [
        "shadow", "dragon", "master", "summer", "winter", "orange", "yellow",
        "football", "baseball", "soccer", "guitar", "planet", "guitar", "rocket",
        "tiger", "coffee", "music", "castle", "knight", "silver", "golden",
        "matrix", "wizard", "london", "paris", "tokyo", "boston", "miami"
    ]
    for _ in range(samples_per_class):
        mode = random.randint(1, 5)
        word = random.choice(c1_words)
        if mode == 1:
            # Word + 1-2 digits
            num = random.randint(1, 99)
            pwd = f"{word}{num}"
        elif mode == 2:
            # Capitalized word + year
            year = random.randint(1980, 2024)
            pwd = f"{word.capitalize()}{year}"
        elif mode == 3:
            # Simple lowercase + single symbol
            sym = random.choice("!@#$")
            num = random.randint(1, 9)
            pwd = f"{word}{sym}{num}"
        elif mode == 4:
            # 7-8 char mixed alphanumeric without special characters
            length = random.randint(7, 8)
            pwd = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=length))
        else:
            # Adversarial: Long but weak multi-word dictionary phrase (16-24 chars, low entropy, single class)
            w1 = random.choice(c1_words)
            w2 = random.choice(c1_words)
            num = random.randint(10, 99)
            pwd = f"{w1}{w2}{num}"
        data.append({"password": pwd, "label": 1})

    # -------------------------------------------------------------
    # Class 2: Moderate (8-14 chars, 2-3 types, leetspeak, or moderate passphrases)
    # -------------------------------------------------------------
    for _ in range(samples_per_class):
        mode = random.randint(1, 5)
        word = random.choice(c1_words)
        if mode == 1:
            # Word with leet substitution + symbol + digits (8-11 chars)
            leet_word = word.replace("a", "@").replace("o", "0").replace("e", "3").replace("i", "1")
            sym = random.choice(["!", "#", "$", "%", "*"])
            num = random.randint(10, 99)
            pwd = f"{leet_word.capitalize()}{sym}{num}"
        elif mode == 2:
            # Two short words combined with a delimiter and digit
            w1 = random.choice(["Red", "Blue", "Fast", "Dark", "Sun", "Sky", "Star"])
            w2 = random.choice(["Fox", "Cat", "Dog", "Bird", "Tree", "Moon", "Sea"])
            num = random.randint(10, 99)
            sym = random.choice(["-", "_", "!", "#"])
            pwd = f"{w1}{sym}{w2}{num}"
        elif mode == 3:
            # Mixed random 9-11 chars containing upper, lower, digits
            chars = random.choices("abcdefghijklmnopqrstuvwxyz", k=5) + \
                    random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=2) + \
                    random.choices("0123456789", k=3)
            random.shuffle(chars)
            pwd = "".join(chars)
        elif mode == 4:
            # 9-10 char password with 1 special symbol
            chars = random.choices("abcdefghijklmnopqrstuvwxyz", k=5) + \
                    random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=2) + \
                    random.choices("0123456789", k=2) + \
                    random.choices("!@#$%^&*", k=1)
            random.shuffle(chars)
            pwd = "".join(chars)
        else:
            # Longer phrase (14-18 chars) but limited to 2 character classes (e.g. 'blue-sky-green-tree')
            w1 = random.choice(["blue", "green", "happy", "golden", "silent", "rapid"])
            w2 = random.choice(["river", "cloud", "meadow", "forest", "harbor", "canyon"])
            sep = random.choice(["-", "_", "."])
            num = random.randint(10, 99)
            pwd = f"{w1}{sep}{w2}{sep}{num}"
        data.append({"password": pwd, "label": 2})

    # -------------------------------------------------------------
    # Class 3: Strong (10-15 chars, 4 types, high entropy, or structured strong passphrases)
    # -------------------------------------------------------------
    specials = "!@#$%^&*()-_=+[]{}|;:,.<>?"
    for _ in range(samples_per_class):
        mode = random.randint(1, 4)
        if mode == 1:
            # Fully randomized 12-14 characters with all 4 classes guaranteed
            k_lower = random.randint(4, 5)
            k_upper = random.randint(3, 4)
            k_digits = random.randint(2, 3)
            k_spec = random.randint(2, 3)
            pool = (
                random.choices("abcdefghijklmnopqrstuvwxyz", k=k_lower) +
                random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=k_upper) +
                random.choices("0123456789", k=k_digits) +
                random.choices(specials, k=k_spec)
            )
            random.shuffle(pool)
            pwd = "".join(pool)
        elif mode == 2:
            # Three-word passphrase with symbols and numbers (13-15 chars)
            w1 = random.choice(["Cobalt", "Falcon", "Nebula", "Quantum", "Vortex"])
            w2 = random.choice(["Shield", "Matrix", "Knight", "Bridge", "Vector"])
            num = random.randint(10, 99)
            sym1 = random.choice(["!", "#", "$", "%"])
            sym2 = random.choice(["&", "*", "@", "?"])
            pwd = f"{w1}{sym1}{w2}{num}{sym2}"
        elif mode == 3:
            # Compact high-entropy random string (10-12 chars, 4 types, e.g. '8#xK!2$vL9@q')
            k_chars = (
                random.choices("abcdefghjkmnpqrstuvwxyz", k=4) +
                random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ", k=3) +
                random.choices("23456789", k=2) +
                random.choices("!@#$%^&*", k=2)
            )
            random.shuffle(k_chars)
            pwd = "".join(k_chars)
        else:
            # 14-char mixed pseudorandom string
            k_chars = (
                random.choices("abcdefghjkmnpqrstuvwxyz", k=5) +
                random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ", k=4) +
                random.choices("23456789", k=3) +
                random.choices("!@#$%^&*", k=2)
            )
            random.shuffle(k_chars)
            pwd = "".join(k_chars)
        data.append({"password": pwd, "label": 3})

    # -------------------------------------------------------------
    # Class 4: Very Strong (16+ chars, ultra-high entropy, multi-word or token)
    # -------------------------------------------------------------
    diceware_words = [
        "correct", "horse", "battery", "staple", "thunder", "glacier", "mountain",
        "horizon", "solitude", "velocity", "acoustic", "dynamo", "element", "friction",
        "gravity", "latitude", "magnetic", "nitrogen", "orbit", "platinum", "radiation"
    ]
    for _ in range(samples_per_class):
        mode = random.randint(1, 3)
        if mode == 1:
            # 4-word diceware passphrase with random separators, numbers & symbols (18-26 chars)
            chosen_words = random.sample(diceware_words, 4)
            sep = random.choice(["-", "_", ".", "#", "$"])
            num = random.randint(10, 99)
            sym = random.choice(["!", "*", "@", "?", "%"])
            pwd = f"{chosen_words[0].capitalize()}{sep}{chosen_words[1]}{sep}{chosen_words[2]}{sep}{chosen_words[3]}{num}{sym}"
        elif mode == 2:
            # High-entropy random 18-22 char alphanumeric + symbol string
            k_len = random.randint(18, 22)
            k_lower = random.randint(5, 7)
            k_upper = random.randint(4, 6)
            k_digits = random.randint(4, 5)
            k_spec = k_len - (k_lower + k_upper + k_digits)
            pool = (
                random.choices("abcdefghijklmnopqrstuvwxyz", k=k_lower) +
                random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=k_upper) +
                random.choices("0123456789", k=k_digits) +
                random.choices(specials, k=k_spec)
            )
            random.shuffle(pool)
            pwd = "".join(pool)
        else:
            # 20+ char cryptographically inspired structured token
            prefix = "".join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ", k=4))
            mid = "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=6))
            digits = "".join(random.choices("0123456789", k=4))
            syms = "".join(random.choices("!@#$%^&*()-_=+", k=4))
            suffix = "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=4))
            chars = list(prefix + mid + digits + syms + suffix)
            random.shuffle(chars)
            pwd = "".join(chars)
        data.append({"password": pwd, "label": 4})

    df = pd.DataFrame(data)
    # Shuffle entire dataset
    df = df.sample(frac=1.0, random_state=random_seed).reset_index(drop=True)
    return df


def preprocess_and_split(df: pd.DataFrame, test_size: float = 0.20, random_seed: int = 42):
    """
    Extracts features for all records, executes stratified train/test split,
    and fits StandardScaler strictly on the training set to prevent data leakage.
    """
    extractor = FeatureExtractor()
    print(f"[*] Extracting 20 numerical features for {len(df)} samples...")

    feature_df = extractor.extract_batch(df["password"].tolist())
    X = feature_df[FEATURE_COLUMNS].to_numpy(dtype=np.float64)
    y = np.array(df["label"].tolist(), dtype=np.int64)
    passwords = np.array(df["password"].tolist(), dtype=object)

    print(f"[*] Executing stratified train-test split (test_size={test_size})...")
    X_train, X_test, y_train, y_test, p_train, p_test = train_test_split(
        X, y, passwords, test_size=test_size, random_state=random_seed, stratify=y
    )

    print("[*] Fitting StandardScaler strictly on training set...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Save to disk
    DATASET_DIR.mkdir(parents=True, exist_ok=True)
    SAVED_MODEL_DIR.mkdir(parents=True, exist_ok=True)

    # Convert arrays back to DataFrame for clean CSV persistence
    train_df = pd.DataFrame(X_train, columns=FEATURE_COLUMNS)
    train_df["label"] = y_train

    test_df = pd.DataFrame(X_test, columns=FEATURE_COLUMNS)
    test_df["label"] = y_test

    train_path = DATASET_DIR / "train.csv"
    test_path = DATASET_DIR / "test.csv"
    train_df.to_csv(train_path, index=False)
    test_df.to_csv(test_path, index=False)

    # Save sample passwords and labels for verification / defense inspection
    sample_df = pd.DataFrame({
        "sample_password_masked": [p[:2] + "*" * max(1, len(p) - 4) + p[-2:] if len(p) >= 4 else "***" for p in p_test[:100]],
        "length": [len(p) for p in p_test[:100]],
        "ground_truth_label": y_test[:100],
        "category_name": [STRENGTH_LABELS[val] for val in y_test[:100]]
    })
    sample_df.to_csv(DATASET_DIR / "test_sample_metadata.csv", index=False)

    # Save scaler artifact
    scaler_path = SAVED_MODEL_DIR / "scaler.joblib"
    joblib.dump(scaler, scaler_path)

    # Save metadata summary
    class_distribution = {STRENGTH_LABELS[i]: int(np.sum(y == i)) for i in range(5)}
    meta = {
        "total_samples": len(df),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "num_features": len(FEATURE_COLUMNS),
        "feature_names": FEATURE_COLUMNS,
        "class_distribution": class_distribution,
        "random_seed": random_seed
    }
    with open(DATASET_DIR / "dataset_summary.json", "w") as f:
        json.dump(meta, f, indent=4)

    print(f"[+] Dataset preparation complete:")
    print(f"    - Total Samples: {len(df):,}")
    print(f"    - Training Set: {len(X_train):,}")
    print(f"    - Test Set: {len(X_test):,}")
    print(f"    - Train CSV saved: {train_path}")
    print(f"    - Test CSV saved: {test_path}")
    print(f"    - Scaler saved: {scaler_path}")
    return X_train_scaled, X_test_scaled, y_train, y_test, scaler


if __name__ == "__main__":
    print("[*] Generating empirical password dataset...")
    raw_df = generate_empirical_dataset(samples_per_class=1000, random_seed=42)
    preprocess_and_split(raw_df)
