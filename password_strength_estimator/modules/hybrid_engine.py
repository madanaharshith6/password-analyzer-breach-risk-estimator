"""
Hybrid Prediction Engine
Synthesizes rule-based heuristics, machine learning inference, and breach-risk feeds
with strict cybersecurity override safeguards.
"""

from typing import Dict, Any, List
import pandas as pd
from modules.password_rules import PasswordRuleEngine
from modules.feature_extraction import FeatureExtractor
from modules.ml_model import MLPasswordModel
from modules.breach_checker import BreachRiskEstimator
from modules.recommendations import RecommendationEngine
from config import STRENGTH_LABELS, STRENGTH_COLORS


class HybridStrengthEngine:
    """
    Unified evaluation engine delivering hybrid password strength estimation,
    vulnerability detection, and breach-risk analysis.
    """

    def __init__(self, ml_model: MLPasswordModel = None):
        self.rule_engine = PasswordRuleEngine()
        self.feature_extractor = FeatureExtractor()
        self.ml_model = ml_model or MLPasswordModel()
        self.breach_estimator = BreachRiskEstimator()
        self.recommendation_engine = RecommendationEngine()

    def analyze(self, password: str) -> Dict[str, Any]:
        """
        Execute full multi-tier hybrid analysis on a given password string.
        Raw password is only processed in-memory for immediate evaluation and is never saved.
        """
        if not password:
            empty_rule = self.rule_engine.evaluate("")
            empty_breach = self.breach_estimator.evaluate_breach_risk("", empty_rule)
            empty_recs = self.recommendation_engine.generate(empty_rule, empty_breach)
            return {
                "password_length": 0,
                "rule_based_score": 0.0,
                "rule_based_category": "Very Weak",
                "ml_prediction_class": 0,
                "ml_prediction_label": "Very Weak",
                "ml_confidence": 0.0,
                "ml_probabilities": {label: 0.0 for label in STRENGTH_LABELS.values()},
                "hybrid_score": 0.0,
                "hybrid_category": "Very Weak",
                "hybrid_color": STRENGTH_COLORS["Very Weak"],
                "breach_assessment": empty_breach,
                "rule_details": empty_rule,
                "features": {col: 0.0 for col in self.feature_extractor.extract_dict("")},
                "identified_weaknesses": ["No password supplied"],
                "recommendations": empty_recs,
                "safeguard_override": False,
                "safeguard_reason": None
            }

        # 1. Rule-Based Evaluation
        rule_results = self.rule_engine.evaluate(password)

        # 2. Numerical Feature Extraction (Standardized Vector)
        features_dict = self.feature_extractor.extract_dict(password)
        features_df = self.feature_extractor.extract_dataframe(password)

        # 3. Machine Learning Inference
        ml_results = self.ml_model.predict(features_df)

        # 4. Breach-Risk Estimation (k-Anonymity & Local Blacklist)
        breach_results = self.breach_estimator.evaluate_breach_risk(password, rule_results)

        # 5. Hybrid Synthesis and Cybersecurity Safeguard Arbitration
        rule_score = rule_results["score"]  # 0 to 100
        rule_scaled = rule_score / 25.0      # 0 to 4.0 scale

        # Calculate ML expected value if probabilities exist
        probs = ml_results["probabilities"]
        label_to_val = {"Very Weak": 0, "Weak": 1, "Moderate": 2, "Strong": 3, "Very Strong": 4}
        ml_expected_val = sum(label_to_val.get(k, 0) * v for k, v in probs.items())

        # Determine Fusion Weights
        if ml_results["model_available"]:
            # Balanced fusion: 45% Rule heuristics, 55% ML probability distribution
            w_rule = 0.45
            w_ml = 0.55
            hybrid_raw = (w_rule * rule_scaled) + (w_ml * ml_expected_val)
        else:
            hybrid_raw = rule_scaled

        # Baseline Hybrid Score (0 to 100)
        hybrid_score = round(min(100.0, max(0.0, hybrid_raw * 25.0)), 1)

        # =========================================================================
        # CRITICAL CYBERSECURITY SAFEGUARDS:
        # A password compromised in data breaches or common dictionary lists
        # must NEVER be rated Moderate, Strong, or Very Strong.
        # =========================================================================
        safeguard_override = False
        safeguard_reason = None

        if breach_results["is_compromised"]:
            safeguard_override = True
            safeguard_reason = "Known Compromised Credential (Identified in Public Breach Database)"
            hybrid_score = min(hybrid_score, 18.0)
            hybrid_category = "Very Weak"
        elif rule_results["score"] < 25.0:
            # Security Weakest-Link Principle: If rule heuristics uncover extreme repetition,
            # sequences, or zero entropy, an optimistic ML model cannot inflate to Moderate/Strong.
            safeguard_override = True
            safeguard_reason = "Structural Vulnerability Override (Low Entropy, Sequence, or Monotonous Pattern)"
            hybrid_score = min(hybrid_score, rule_results["score"] + 6.0, 24.0)
            hybrid_category = "Very Weak"
        elif len(password) < 8:
            # Absolute Length Threshold: Any credential under 8 characters can be brute-forced in seconds
            safeguard_override = True
            safeguard_reason = f"Inadequate Password Length ({len(password)} characters; <8 cannot exceed Weak tier)"
            hybrid_score = min(hybrid_score, 38.0)
            hybrid_category = "Weak" if hybrid_score >= 25.0 else "Very Weak"
        elif rule_results["dictionary_matches"] and len(password) < 12:
            safeguard_override = True
            safeguard_reason = f"Contains Common Dictionary Root ({', '.join(rule_results['dictionary_matches'])})"
            hybrid_score = min(hybrid_score, 38.0)
            hybrid_category = "Weak" if hybrid_score >= 25.0 else "Very Weak"
        elif rule_results["has_keyboard_sequence"] and len(password) < 10:
            safeguard_override = True
            safeguard_reason = "Contains Keyboard Walk Pattern with Short Length"
            hybrid_score = min(hybrid_score, 35.0)
            hybrid_category = "Weak" if hybrid_score >= 25.0 else "Very Weak"
        else:
            # Map continuous score to 5 tiers
            if hybrid_score < 25.0:
                hybrid_category = "Very Weak"
            elif hybrid_score < 45.0:
                hybrid_category = "Weak"
            elif hybrid_score < 65.0:
                hybrid_category = "Moderate"
            elif hybrid_score < 85.0:
                hybrid_category = "Strong"
            else:
                hybrid_category = "Very Strong"

        # 6. Generate Actionable Security Recommendations
        recommendations = self.recommendation_engine.generate(rule_results, breach_results)

        # 7. Compile Identified Weaknesses
        weaknesses = []
        if safeguard_override:
            weaknesses.append(f"Security Alert: {safeguard_reason}")
        for failed in rule_results["rules_failed"]:
            weaknesses.append(failed)
        for penalty in rule_results["penalties"]:
            if penalty not in weaknesses:
                weaknesses.append(penalty)

        return {
            "password_length": len(password),
            "rule_based_score": rule_score,
            "rule_based_category": rule_results["category"],
            "ml_prediction_class": ml_results["predicted_class"],
            "ml_prediction_label": ml_results["predicted_label"],
            "ml_confidence": ml_results["confidence"],
            "ml_probabilities": ml_results["probabilities"],
            "ml_model_name": ml_results.get("model_name", "N/A"),
            "ml_available": ml_results["model_available"],
            "hybrid_score": hybrid_score,
            "hybrid_category": hybrid_category,
            "hybrid_color": STRENGTH_COLORS.get(hybrid_category, "#888888"),
            "breach_assessment": breach_results,
            "rule_details": rule_results,
            "features": features_dict,
            "identified_weaknesses": weaknesses,
            "recommendations": recommendations,
            "safeguard_override": safeguard_override,
            "safeguard_reason": safeguard_reason
        }
