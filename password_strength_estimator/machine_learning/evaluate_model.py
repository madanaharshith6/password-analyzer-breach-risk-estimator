"""
Model Evaluation and Publication Artifacts Engine
Evaluates models across standard holdout splits and the independent Challenging Adversarial Holdout Dataset.
Generates comprehensive academic performance reports, confusion matrices, and publication charts.
"""

import os
import sys
import json
from pathlib import Path
import numpy as np
import pandas as pd
import joblib

# Plotting libraries
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns

# Metrics
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score

# Root directory configuration
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from config import DATASET_DIR, SAVED_MODEL_DIR, MODEL_FILE, METRICS_FILE, ASSETS_DIR, FEATURE_COLUMNS, STRENGTH_LABELS
from modules.feature_extraction import FeatureExtractor

# Set matplotlib cache directory to avoid permissions issues
os.environ["MPLCONFIGDIR"] = str(ASSETS_DIR / "mpl_cache")
(ASSETS_DIR / "mpl_cache").mkdir(parents=True, exist_ok=True)


def evaluate_and_plot():
    """
    Evaluates the saved champion model on both:
    1. Standard unseen test split (1,000 samples)
    2. Independent Challenging Adversarial Holdout Dataset (250 out-of-distribution samples)
    Generates publication-ready visual artifacts.
    """
    if not MODEL_FILE.exists():
        print(f"[!] Error: Model file {MODEL_FILE} not found. Please run train_model.py first.")
        sys.exit(1)

    test_path = DATASET_DIR / "test.csv"
    holdout_path = DATASET_DIR / "challenging_holdout.csv"
    if not test_path.exists():
        print(f"[!] Error: Test data {test_path} not found.")
        sys.exit(1)

    print("=" * 75)
    print("           MACHINE LEARNING RIGOROUS INDEPENDENT AUDIT & EVALUATION")
    print("=" * 75)

    # Load bundle
    bundle = joblib.load(MODEL_FILE)
    model = bundle["model"]
    scaler = bundle["scaler"]
    model_name = bundle["model_name"]
    benchmarks = bundle.get("benchmark_metrics", {})

    # Load standard test data
    test_df = pd.read_csv(test_path)
    X_test_raw = test_df[FEATURE_COLUMNS].to_numpy(dtype=float)
    y_test = test_df["label"].to_numpy(dtype=int)

    # Transform features
    X_test = scaler.transform(X_test_raw)
    y_pred = model.predict(X_test)

    # Standard metrics
    acc = accuracy_score(y_test, y_pred)
    f1_weighted = f1_score(y_test, y_pred, average="weighted", zero_division=0)
    f1_macro = f1_score(y_test, y_pred, average="macro", zero_division=0)

    print(f"\n[+] Champion Architecture: {model_name}")
    print(f"[+] Total Standard Test Samples:    {len(y_test):,}")
    print(f"[+] Empirical Test Accuracy:         {acc * 100:.2f}%")
    print(f"[+] Weighted F1-Score:               {f1_weighted * 100:.2f}%")
    print(f"[+] Macro F1-Score:                  {f1_macro * 100:.2f}%\n")

    class_names = [STRENGTH_LABELS[i] for i in range(5)]
    print("-" * 75)
    print("         STANDARD TEST SPLIT CLASSIFICATION REPORT")
    print("-" * 75)
    print(classification_report(y_test, y_pred, target_names=class_names, digits=4))

    # Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    header_title = "Actual \\ Predicted"
    print("-" * 75)
    print("                 STANDARD CONFUSION MATRIX")
    print("-" * 75)
    print(f"{header_title:<20} " + " ".join([f"{name[:8]:>8}" for name in class_names]))
    for i, row in enumerate(cm):
        row_str = " ".join([f"{val:>8}" for val in row])
        print(f"{class_names[i]:<20} {row_str}")
    print("-" * 75)

    # -------------------------------------------------------------
    # Independent Challenging Adversarial Holdout Evaluation
    # -------------------------------------------------------------
    if holdout_path.exists():
        holdout_df = pd.read_csv(holdout_path)
        extractor = FeatureExtractor()
        X_h_raw = extractor.extract_batch(holdout_df["password"].tolist())[FEATURE_COLUMNS].to_numpy(dtype=float)
        X_holdout = scaler.transform(X_h_raw)
        y_holdout = holdout_df["ground_truth_label"].to_numpy(dtype=int)

        y_h_pred = model.predict(X_holdout)
        h_acc = accuracy_score(y_holdout, y_h_pred)
        h_f1 = f1_score(y_holdout, y_h_pred, average="weighted", zero_division=0)
        cm_holdout = confusion_matrix(y_holdout, y_h_pred)

        print("\n" + "=" * 75)
        print("    INDEPENDENT CHALLENGING ADVERSARIAL HOLDOUT EVALUATION (OUT-OF-DISTRIBUTION)")
        print(f"    Total Adversarial Samples: {len(y_holdout):,}")
        print(f"    Generalization Accuracy:  {h_acc * 100:.2f}%")
        print(f"    Generalization F1-Score:  {h_f1 * 100:.2f}%")
        print("=" * 75)
        print(classification_report(y_holdout, y_h_pred, target_names=class_names, digits=4))

        print("-" * 75)
        print("          CHALLENGING HOLDOUT CONFUSION MATRIX")
        print("-" * 75)
        print(f"{header_title:<20} " + " ".join([f"{name[:8]:>8}" for name in class_names]))
        for i, row in enumerate(cm_holdout):
            row_str = " ".join([f"{val:>8}" for val in row])
            print(f"{class_names[i]:<20} {row_str}")
        print("-" * 75)

    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    # -------------------------------------------------------------
    # Plot 1: Algorithm Benchmark Comparison Bar Chart
    # -------------------------------------------------------------
    if benchmarks:
        print("\n[*] Generating Algorithm Comparison Chart...")
        models = list(benchmarks.keys())
        test_accs = [benchmarks[m]["accuracy"] * 100 for m in models]
        holdout_accs = [benchmarks[m].get("holdout_accuracy", 0.0) * 100 for m in models]
        cv_scores = [benchmarks[m]["cv_mean_accuracy"] * 100 for m in models]

        x = np.arange(len(models))
        width = 0.25

        plt.figure(figsize=(10, 6))
        plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
        fig, ax = plt.subplots(figsize=(10, 5.5))

        rects1 = ax.bar(x - width, test_accs, width, label="Standard Test Accuracy", color="#1E88E5")
        rects2 = ax.bar(x, cv_scores, width, label="5-Fold CV Accuracy", color="#FB8C00")
        rects3 = ax.bar(x + width, holdout_accs, width, label="Adversarial Holdout Accuracy", color="#E53935")

        ax.set_ylabel("Accuracy (%)", fontsize=11, fontweight="bold")
        ax.set_title("Algorithm Performance: Standard vs Adversarial Holdout", fontsize=12, fontweight="bold", pad=12)
        ax.set_xticks(x)
        ax.set_xticklabels(models, fontsize=9.5, fontweight="bold")
        ax.set_ylim(45, 108)
        ax.legend(frameon=True, loc="upper right")

        def autolabel(rects):
            for rect in rects:
                height = rect.get_height()
                ax.annotate(f"{height:.1f}%",
                            xy=(rect.get_x() + rect.get_width() / 2, height),
                            xytext=(0, 3),
                            textcoords="offset points",
                            ha="center", va="bottom", fontsize=7.5, fontweight="bold")

        autolabel(rects1)
        autolabel(rects2)
        autolabel(rects3)

        plt.tight_layout()
        chart_path = ASSETS_DIR / "algorithm_comparison.png"
        plt.savefig(chart_path, dpi=300)
        plt.close()
        print(f"[+] Saved Algorithm Comparison Plot: {chart_path}")

    # -------------------------------------------------------------
    # Plot 2: Standard Confusion Matrix Heatmap
    # -------------------------------------------------------------
    print("[*] Generating Standard Confusion Matrix Heatmap...")
    plt.figure(figsize=(7, 6))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=class_names,
        yticklabels=class_names,
        cbar=True,
        annot_kws={"size": 11, "weight": "bold"}
    )
    plt.title(f"Standard Test Confusion Matrix ({model_name})", fontsize=11, fontweight="bold", pad=12)
    plt.xlabel("Predicted Label", fontsize=10, fontweight="bold")
    plt.ylabel("Ground Truth Label", fontsize=10, fontweight="bold")
    plt.tight_layout()
    cm_path = ASSETS_DIR / "confusion_matrix.png"
    plt.savefig(cm_path, dpi=300)
    plt.close()
    print(f"[+] Saved Standard Confusion Matrix Heatmap: {cm_path}")

    # -------------------------------------------------------------
    # Plot 3: Challenging Holdout Confusion Matrix Heatmap
    # -------------------------------------------------------------
    if holdout_path.exists():
        print("[*] Generating Challenging Holdout Confusion Matrix Heatmap...")
        plt.figure(figsize=(7, 6))
        sns.heatmap(
            cm_holdout,
            annot=True,
            fmt="d",
            cmap="Reds",
            xticklabels=class_names,
            yticklabels=class_names,
            cbar=True,
            annot_kws={"size": 11, "weight": "bold"}
        )
        plt.title(f"Adversarial Holdout Confusion Matrix ({model_name})", fontsize=11, fontweight="bold", pad=12)
        plt.xlabel("Predicted Label", fontsize=10, fontweight="bold")
        plt.ylabel("Ground Truth Label", fontsize=10, fontweight="bold")
        plt.tight_layout()
        cm_h_path = ASSETS_DIR / "holdout_confusion_matrix.png"
        plt.savefig(cm_h_path, dpi=300)
        plt.close()
        print(f"[+] Saved Adversarial Holdout Confusion Matrix Heatmap: {cm_h_path}")

    # -------------------------------------------------------------
    # Plot 4: Feature Importance / Coefficients
    # -------------------------------------------------------------
    print("[*] Generating Feature Importance / Weight Chart...")
    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
        title = f"Top Predictive Features (Gini Importance - {model_name})"
    elif hasattr(model, "coef_"):
        # Mean absolute coefficient across all 5 classes for Logistic Regression
        importances = np.mean(np.abs(model.coef_), axis=0)
        title = f"Top Predictive Feature Weights (|Mean Coefficient| - {model_name})"
    else:
        importances = None

    if importances is not None:
        feat_df = pd.DataFrame({"Feature": FEATURE_COLUMNS, "Importance": importances})
        feat_df = feat_df.sort_values(by="Importance", ascending=False).head(12)

        plt.figure(figsize=(9, 5.5))
        sns.barplot(x="Importance", y="Feature", data=feat_df, color="#1976D2")
        plt.title(title, fontsize=11, fontweight="bold", pad=12)
        plt.xlabel("Relative Predictive Weight", fontsize=10, fontweight="bold")
        plt.ylabel("Extracted Feature", fontsize=10, fontweight="bold")
        plt.tight_layout()
        feat_path = ASSETS_DIR / "feature_importance.png"
        plt.savefig(feat_path, dpi=300)
        plt.close()
        print(f"[+] Saved Feature Importance Chart: {feat_path}")

    print("\n[+] Rigorous Model Evaluation & Visual Artifacts Generation Completed Successfully!")


if __name__ == "__main__":
    evaluate_and_plot()
