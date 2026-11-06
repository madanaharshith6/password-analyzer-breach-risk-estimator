"""
Machine Learning Model Wrapper
Loads serialized model pipelines, validates numerical features, and performs inference.
"""

from pathlib import Path
from typing import Dict, Any, Optional
import joblib
import numpy as np
import pandas as pd
from config import MODEL_FILE, STRENGTH_LABELS, FEATURE_COLUMNS


class MLPasswordModel:
    """
    Production wrapper for the trained machine learning password strength classifier.
    Ensures safe inference using only numerical features and never raw passwords.
    """

    def __init__(self, model_path: Optional[Path] = None):
        self.model_path = model_path or MODEL_FILE
        self.model = None
        self.scaler = None
        self.model_name = "Uninitialized"
        self.benchmark_metrics = {}
        self.feature_names = FEATURE_COLUMNS
        self.is_loaded = False
        self.load_model()

    def load_model(self) -> bool:
        """Load serialized model bundle from disk."""
        if Path(self.model_path).exists():
            try:
                bundle = joblib.load(self.model_path)
                self.model = bundle.get("model")
                self.scaler = bundle.get("scaler")
                self.model_name = bundle.get("model_name", "Trained ML Model")
                self.benchmark_metrics = bundle.get("benchmark_metrics", {})
                self.feature_names = bundle.get("feature_names", FEATURE_COLUMNS)
                self.is_loaded = True
                return True
            except Exception as e:
                print(f"[Warning] Failed loading ML model from {self.model_path}: {e}")
                self.is_loaded = False
                return False
        else:
            self.is_loaded = False
            return False

    def predict(self, features_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Execute prediction on numerical feature vector.
        Features must match the 20 columns defined in FEATURE_COLUMNS.
        """
        if not self.is_loaded:
            # Fallback if model hasn't been trained yet
            return {
                "predicted_class": 0,
                "predicted_label": "Model Not Loaded",
                "probabilities": {label: 0.2 for label in STRENGTH_LABELS.values()},
                "confidence": 0.0,
                "model_available": False
            }

        # Align features to ensure exact ordering
        X = features_df[self.feature_names].to_numpy(dtype=float)

        # Apply standard scaling if scaler exists
        if self.scaler is not None:
            X_scaled = self.scaler.transform(X)
        else:
            X_scaled = X

        # Model inference
        pred_class = int(self.model.predict(X_scaled)[0])
        pred_label = STRENGTH_LABELS.get(pred_class, "Unknown")

        # Probability distribution
        if hasattr(self.model, "predict_proba"):
            probs_raw = self.model.predict_proba(X_scaled)[0]
            classes = self.model.classes_
            probs = {}
            for i, cls_idx in enumerate(classes):
                label = STRENGTH_LABELS.get(int(cls_idx), f"Class {cls_idx}")
                probs[label] = round(float(probs_raw[i]), 4)
            confidence = float(np.max(probs_raw))
        elif hasattr(self.model, "decision_function"):
            decision = self.model.decision_function(X_scaled)[0]
            # Softmax approximation for decision function
            exp_d = np.exp(decision - np.max(decision))
            probs_raw = exp_d / np.sum(exp_d)
            probs = {STRENGTH_LABELS.get(i, f"Class {i}"): round(float(p), 4) for i, p in enumerate(probs_raw)}
            confidence = float(np.max(probs_raw))
        else:
            probs = {label: (1.0 if label == pred_label else 0.0) for label in STRENGTH_LABELS.values()}
            confidence = 1.0

        return {
            "predicted_class": pred_class,
            "predicted_label": pred_label,
            "probabilities": probs,
            "confidence": round(confidence, 4),
            "model_name": self.model_name,
            "model_available": True
        }

    def get_feature_importances(self) -> Optional[Dict[str, float]]:
        """Return feature importances if the model is tree-based."""
        if not self.is_loaded or self.model is None:
            return None
        if hasattr(self.model, "feature_importances_"):
            importances = self.model.feature_importances_
            return {name: round(float(imp), 4) for name, imp in zip(self.feature_names, importances)}
        return None
