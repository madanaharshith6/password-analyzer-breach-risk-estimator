"""
Model Training and Algorithm Comparison Engine
Trains, cross-validates, and compares 4 machine learning algorithms on genuine numerical features.
Selects and serializes the champion model based on empirical F1-Score and Accuracy.
"""

import os
import sys
import time
import json
from pathlib import Path
import numpy as np
import pandas as pd
import joblib

# ML imports
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

# Root directory configuration
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from config import DATASET_DIR, SAVED_MODEL_DIR, MODEL_FILE, METRICS_FILE, FEATURE_COLUMNS, STRENGTH_LABELS, ASSETS_DIR
from machine_learning.preprocessing import generate_empirical_dataset, preprocess_and_split
from machine_learning.create_holdout import build_challenging_holdout
from modules.feature_extraction import FeatureExtractor

# Safe cache dir for matplotlib
os.environ["MPLCONFIGDIR"] = str(ASSETS_DIR / "mpl_cache")


def train_and_compare_models(force_regenerate_data: bool = True):
    """
    Executes training and cross-validation across 4 standard classification algorithms:
    1. Logistic Regression
    2. Decision Tree
    3. Random Forest
    4. Support Vector Machine (LinearSVC with Calibrated Probabilities)
    Evaluates both on standard holdout test split AND on the independent Challenging Adversarial Holdout Dataset.
    """
    train_path = DATASET_DIR / "train.csv"
    test_path = DATASET_DIR / "test.csv"
    scaler_path = SAVED_MODEL_DIR / "scaler.joblib"
    holdout_path = DATASET_DIR / "challenging_holdout.csv"

    if force_regenerate_data or not train_path.exists() or not test_path.exists() or not scaler_path.exists():
        print("[*] Generating enhanced empirical dataset with adversarial long/short structures...")
        raw_df = generate_empirical_dataset(samples_per_class=1000, random_seed=42)
        preprocess_and_split(raw_df)

    if not holdout_path.exists():
        build_challenging_holdout()

    # Load data
    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)
    holdout_df = pd.read_csv(holdout_path)
    scaler = joblib.load(scaler_path)

    X_train_raw = train_df[FEATURE_COLUMNS].to_numpy(dtype=float)
    y_train = train_df["label"].to_numpy(dtype=int)

    X_test_raw = test_df[FEATURE_COLUMNS].to_numpy(dtype=float)
    y_test = test_df["label"].to_numpy(dtype=int)

    # Scale features
    X_train = scaler.transform(X_train_raw)
    X_test = scaler.transform(X_test_raw)

    # Extract & scale features for the challenging holdout dataset
    extractor = FeatureExtractor()
    X_holdout_raw = extractor.extract_batch(holdout_df["password"].tolist())[FEATURE_COLUMNS].to_numpy(dtype=float)
    X_holdout = scaler.transform(X_holdout_raw)
    y_holdout = holdout_df["ground_truth_label"].to_numpy(dtype=int)

    print("=" * 70)
    print("      SUPERVISED MACHINE LEARNING MODEL TRAINING & COMPARISON")
    print(f"      Training Samples: {len(X_train):,} | Test Samples: {len(X_test):,}")
    print(f"      Challenging Adversarial Holdout Samples: {len(X_holdout):,}")
    print(f"      Ground-Truth Classes: 5 (Very Weak -> Very Strong)")
    print("=" * 70)

    # Define the 4 target candidate architectures
    candidates = {
        "Logistic Regression": LogisticRegression(
            max_iter=1000,
            C=1.0,
            solver="lbfgs",
            random_state=42
        ),
        "Decision Tree": DecisionTreeClassifier(
            max_depth=12,
            min_samples_split=5,
            min_samples_leaf=2,
            criterion="gini",
            random_state=42
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=100,
            max_depth=16,
            min_samples_split=4,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        ),
        "Support Vector Machine": CalibratedClassifierCV(
            estimator=LinearSVC(
                C=1.0,
                dual=False,
                max_iter=2500,
                random_state=42
            ),
            cv=3
        )
    }

    benchmark_results = {}
    trained_models = {}
    confusion_matrices = {}
    classification_reports = {}

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    for name, clf in candidates.items():
        print(f"\n[*] Training and Cross-Validating: {name}...")
        start_time = time.time()

        # 5-fold Cross-Validation on Training set
        cv_scores = cross_val_score(clf, X_train, y_train, cv=cv, scoring="accuracy")
        mean_cv_acc = float(np.mean(cv_scores))
        std_cv_acc = float(np.std(cv_scores))

        # Train on full training set
        clf.fit(X_train, y_train)
        train_duration = round(time.time() - start_time, 3)

        # Inference on unseen Test set
        infer_start = time.time()
        y_pred = clf.predict(X_test)
        infer_duration = round((time.time() - infer_start) * 1000 / len(X_test), 3)  # ms per sample

        # Calculate metrics on standard test set
        acc = float(accuracy_score(y_test, y_pred))
        prec_macro = float(precision_score(y_test, y_pred, average="macro", zero_division=0))
        prec_weighted = float(precision_score(y_test, y_pred, average="weighted", zero_division=0))
        rec_macro = float(recall_score(y_test, y_pred, average="macro", zero_division=0))
        rec_weighted = float(recall_score(y_test, y_pred, average="weighted", zero_division=0))
        f1_m = float(f1_score(y_test, y_pred, average="macro", zero_division=0))
        f1_w = float(f1_score(y_test, y_pred, average="weighted", zero_division=0))

        cm = confusion_matrix(y_test, y_pred).tolist()
        report = classification_report(
            y_test, y_pred,
            target_names=[STRENGTH_LABELS[i] for i in range(5)],
            output_dict=True,
            zero_division=0
        )

        # Independent Evaluation on Challenging Adversarial Holdout Dataset
        y_holdout_pred = clf.predict(X_holdout)
        holdout_acc = float(accuracy_score(y_holdout, y_holdout_pred))
        holdout_f1 = float(f1_score(y_holdout, y_holdout_pred, average="weighted", zero_division=0))
        holdout_prec = float(precision_score(y_holdout, y_holdout_pred, average="weighted", zero_division=0))
        holdout_rec = float(recall_score(y_holdout, y_holdout_pred, average="weighted", zero_division=0))
        holdout_cm = confusion_matrix(y_holdout, y_holdout_pred).tolist()

        trained_models[name] = clf
        confusion_matrices[name] = cm
        classification_reports[name] = report

        benchmark_results[name] = {
            "accuracy": round(acc, 4),
            "cv_mean_accuracy": round(mean_cv_acc, 4),
            "cv_std_accuracy": round(std_cv_acc, 4),
            "precision_macro": round(prec_macro, 4),
            "precision_weighted": round(prec_weighted, 4),
            "recall_macro": round(rec_macro, 4),
            "recall_weighted": round(rec_weighted, 4),
            "f1_macro": round(f1_m, 4),
            "f1_weighted": round(f1_w, 4),
            "train_time_sec": train_duration,
            "inference_time_ms_per_sample": infer_duration,
            "holdout_accuracy": round(holdout_acc, 4),
            "holdout_f1_weighted": round(holdout_f1, 4),
            "holdout_precision_weighted": round(holdout_prec, 4),
            "holdout_recall_weighted": round(holdout_rec, 4),
            "holdout_confusion_matrix": holdout_cm
        }

        print(f"    - 5-Fold CV Accuracy:            {mean_cv_acc:.4f} (+/- {std_cv_acc:.4f})")
        print(f"    - Test Set Accuracy:             {acc:.4f} | F1: {f1_w:.4f}")
        print(f"    - Challenging Holdout Accuracy:  {holdout_acc:.4f} | F1: {holdout_f1:.4f}")
        print(f"    - Training Time:                 {train_duration} s")

    # Select champion model based on challenging holdout F1-Score + test F1
    best_name = max(benchmark_results.keys(), key=lambda k: benchmark_results[k]["holdout_f1_weighted"] * 0.5 + benchmark_results[k]["f1_weighted"] * 0.5)
    best_model = trained_models[best_name]
    best_metrics = benchmark_results[best_name]

    print("\n" + "=" * 70)
    print(f"[+] CHAMPION MODEL SELECTED: {best_name.upper()}")
    print(f"    - Standard Test Accuracy:        {best_metrics['accuracy']:.4f}")
    print(f"    - Challenging Holdout Accuracy:  {best_metrics['holdout_accuracy']:.4f}")
    print(f"    - Challenging Holdout F1-Score:  {best_metrics['holdout_f1_weighted']:.4f}")
    print("=" * 70)

    # Serialize complete model bundle using Joblib
    SAVED_MODEL_DIR.mkdir(parents=True, exist_ok=True)
    bundle = {
        "model": best_model,
        "scaler": scaler,
        "model_name": best_name,
        "benchmark_metrics": benchmark_results,
        "feature_names": FEATURE_COLUMNS,
        "class_labels": STRENGTH_LABELS,
        "confusion_matrices": confusion_matrices,
        "classification_reports": classification_reports,
        "trained_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    joblib.dump(bundle, MODEL_FILE)
    print(f"[+] Saved serialized model artifact to: {MODEL_FILE}")

    # Export benchmark metrics to JSON for fast parsing by Streamlit frontend
    export_metrics = {
        "champion_model": best_name,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "benchmarks": benchmark_results,
        "confusion_matrices": confusion_matrices,
        "classification_reports": classification_reports
    }
    with open(METRICS_FILE, "w") as f:
        json.dump(export_metrics, f, indent=4)
    print(f"[+] Exported benchmark metrics to: {METRICS_FILE}")

    return best_name, benchmark_results


if __name__ == "__main__":
    train_and_compare_models()
