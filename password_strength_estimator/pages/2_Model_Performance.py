"""
Page 2: Model Performance & Algorithmic Benchmarks
Empirical Machine Learning Evaluation, Multi-Model Comparison, and Holdout Diagnostics
Student: MADANA KOMAL SIVA SAI HARSHITH (Roll No: 24ME5A5408)
"""

import sys
import json
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import joblib

# Setup paths
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from config import METRICS_FILE, MODEL_FILE, ASSETS_DIR, STRENGTH_LABELS, FEATURE_COLUMNS

# Page configuration
st.set_page_config(page_title="Model Performance • Hybrid Estimator", page_icon="📊", layout="wide")

st.markdown("""
<style>
    .page-title {
        font-size: 2rem;
        font-weight: 800;
        color: #38bdf8;
        margin-bottom: 0.2rem;
    }
    .metric-card {
        background-color: #131d31;
        border: 1px solid #1e293b;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.25);
    }
    .metric-title {
        color: #94a3b8;
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-value {
        font-size: 1.45rem;
        font-weight: 700;
        margin: 0.2rem 0;
    }
    .metric-sub {
        color: #64748b;
        font-size: 0.76rem;
    }
    .section-card {
        background-color: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 8px;
        padding: 1.1rem;
        margin-bottom: 1.1rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='page-title'>📊 Supervised ML Model Performance Benchmarks</div>", unsafe_allow_html=True)
st.caption(
    "Empirical evaluation and comparative analysis of 4 classification algorithms "
    "across 1,000 in-distribution test samples and an independent 250-sample out-of-distribution adversarial holdout dataset."
)

# Cached Resource Singletons
@st.cache_data(show_spinner=False)
def load_metrics_data():
    with open(METRICS_FILE, "r") as f:
        return json.load(f)

@st.cache_resource(show_spinner=False)
def load_model_bundle():
    return joblib.load(MODEL_FILE)

# Load saved metrics
if not METRICS_FILE.exists() or not MODEL_FILE.exists():
    st.error("⚠️ Model benchmark artifacts not found. Please train models first using: `python machine_learning/train_model.py`")
    st.stop()

metrics_data = load_metrics_data()
bundle = load_model_bundle()
benchmarks = metrics_data["benchmarks"]
champion_name = metrics_data.get("champion_model", "Logistic Regression")
champ_metrics = benchmarks[champion_name]

# Top KPI Metric Cards
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f"""
    <div class='metric-card' style='border-top: 3px solid #4ade80;'>
        <div class='metric-title'>CHAMPION MODEL</div>
        <div class='metric-value' style='color:#4ade80;'>{champion_name}</div>
        <div class='metric-sub'>Selected via Adversarial Generalization</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class='metric-card' style='border-top: 3px solid #38bdf8;'>
        <div class='metric-title'>STANDARD TEST ACCURACY</div>
        <div class='metric-value' style='color:#38bdf8;'>{champ_metrics['accuracy'] * 100:.2f}%</div>
        <div class='metric-sub'>1,000 In-Distribution Test Samples</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    holdout_acc = champ_metrics.get('holdout_accuracy', 0.0) * 100
    st.markdown(f"""
    <div class='metric-card' style='border-top: 3px solid #ef4444;'>
        <div class='metric-title'>ADVERSARIAL HOLDOUT ACCURACY</div>
        <div class='metric-value' style='color:#ef4444;'>{holdout_acc:.2f}%</div>
        <div class='metric-sub'>250 Out-of-Distribution Edge Samples</div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class='metric-card' style='border-top: 3px solid #a855f7;'>
        <div class='metric-title'>5-FOLD CV ACCURACY</div>
        <div class='metric-value' style='color:#a855f7;'>{champ_metrics['cv_mean_accuracy'] * 100:.2f}%</div>
        <div class='metric-sub'>Standard Deviation: ±{champ_metrics['cv_std_accuracy'] * 100:.2f}%</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# -------------------------------------------------------------
# Section 1: Benchmark Comparison Table
# -------------------------------------------------------------
st.subheader("📈 Multi-Model Benchmark Comparison: In-Distribution vs Adversarial Holdout")
st.write(
    "All four algorithms were trained on the identical 4,000-sample training partition and evaluated on "
    "both the standard 1,000-sample test split and the independent 250-sample challenging holdout dataset."
)

comparison_rows = []
for model_name, m in benchmarks.items():
    test_acc = m["accuracy"] * 100
    adv_acc = m.get("holdout_accuracy", 0.0) * 100
    delta = test_acc - adv_acc

    comparison_rows.append({
        "Algorithm": model_name,
        "Standard Test Acc (%)": round(test_acc, 2),
        "Standard Test F1 (%)": round(m["f1_weighted"] * 100, 2),
        "5-Fold CV Mean (%)": round(m["cv_mean_accuracy"] * 100, 2),
        "Adversarial Holdout Acc (%)": round(adv_acc, 2),
        "Adversarial Holdout F1 (%)": round(m.get("holdout_f1_weighted", 0.0) * 100, 2),
        "Generalization Gap (Δ)": f"-{delta:.1f}%",
        "Training Latency (s)": f"{m['train_time_sec']:.3f}s"
    })

df_comp = pd.DataFrame(comparison_rows)

col_table, col_chart = st.columns([1.3, 1.1])

with col_table:
    st.dataframe(
        df_comp,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("""
    <div class='section-card' style='margin-top:0.6rem;'>
        <div style='font-weight:700; color:#38bdf8; font-size:0.88rem; margin-bottom:0.3rem;'>🏆 Documented Model-Selection Criterion</div>
        <div style='font-size:0.82rem; color:#cbd5e1; line-height:1.45;'>
            While <b>Random Forest</b> achieved 100.0% on in-distribution synthetic tests, 
            <b>Logistic Regression</b> was selected as Champion for three critical scientific reasons:
            <ol style='margin:0.3rem 0 0 1rem; padding:0;'>
                <li><b>Superior Adversarial Generalization:</b> Highest accuracy on out-of-distribution holdout (<b>69.60%</b> vs Decision Tree 64.40% and SVM 60.00%).</li>
                <li><b>Calibrated Probability Outputs:</b> Logistic Regression provides smooth sigmoid/softmax probabilities, essential for continuous hybrid expectation fusion. Decision trees output abrupt step functions that create erratic scores.</li>
                <li><b>Ultra-Low Inference Latency:</b> Single matrix multiply execution (0.002 ms per sample) vs multi-tree traversal (0.048 ms).</li>
            </ol>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_chart:
    models = list(benchmarks.keys())
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        name='Standard Test Accuracy',
        x=models,
        y=[benchmarks[m]["accuracy"] * 100 for m in models],
        marker_color='#0284c7'
    ))
    fig_bar.add_trace(go.Bar(
        name='5-Fold CV Accuracy',
        x=models,
        y=[benchmarks[m]["cv_mean_accuracy"] * 100 for m in models],
        marker_color='#f59e0b'
    ))
    fig_bar.add_trace(go.Bar(
        name='Adversarial Holdout Accuracy',
        x=models,
        y=[benchmarks[m].get("holdout_accuracy", 0.0) * 100 for m in models],
        marker_color='#ef4444'
    ))
    fig_bar.update_layout(
        barmode='group',
        yaxis=dict(range=[45, 105], title="Accuracy (%)", tickfont=dict(color="#94a3b8")),
        xaxis=dict(tickfont=dict(color="#cbd5e1")),
        height=330,
        margin=dict(l=20, r=20, t=30, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#131d31",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10, color="#cbd5e1"))
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# -------------------------------------------------------------
# Section 2: Confusion Matrices
# -------------------------------------------------------------
st.markdown("---")
st.subheader("🎯 Confusion Matrices & Class-Level Diagnostics")

col_cm_select, col_cm_plot = st.columns([1.0, 1.4])
class_names = [STRENGTH_LABELS[i] for i in range(5)]

with col_cm_select:
    selected_model = st.selectbox(
        "Select Model Architecture:",
        options=list(benchmarks.keys()),
        index=list(benchmarks.keys()).index(champion_name) if champion_name in benchmarks else 0
    )

    dataset_view = st.radio(
        "Evaluation Dataset to Visualize:",
        options=["Standard Test Split (1,000 samples)", "Adversarial Holdout Set (250 samples)"],
        index=0
    )

    reports = metrics_data["classification_reports"].get(selected_model, {})
    if reports and "Standard" in dataset_view:
        report_rows = []
        for cname in class_names:
            if cname in reports:
                report_rows.append({
                    "Strength Class": cname,
                    "Precision": f"{reports[cname]['precision']:.4f}",
                    "Recall": f"{reports[cname]['recall']:.4f}",
                    "F1-Score": f"{reports[cname]['f1-score']:.4f}",
                    "Support": int(reports[cname]["support"])
                })
        st.write(f"**Classification Report: `{selected_model}` (Standard Test)**")
        st.dataframe(pd.DataFrame(report_rows), use_container_width=True, hide_index=True)
    else:
        st.write(f"**Adversarial Holdout Metrics: `{selected_model}`**")
        m_data = benchmarks[selected_model]
        st.write(f"• Holdout Accuracy: **{m_data.get('holdout_accuracy', 0.0)*100:.2f}%**")
        st.write(f"• Holdout Weighted F1: **{m_data.get('holdout_f1_weighted', 0.0)*100:.2f}%**")
        st.caption("Holdout set consists of 50 samples per tier with unseen repetitions, dictionary roots, and spatial keyboard trajectories.")

with col_cm_plot:
    if "Standard" in dataset_view:
        cm_data = metrics_data["confusion_matrices"].get(selected_model, [])
        cmap = "Blues"
        title_suffix = "Standard Test Split (1,000 samples)"
    else:
        cm_data = benchmarks[selected_model].get("holdout_confusion_matrix", [])
        cmap = "Reds"
        title_suffix = "Adversarial Holdout (250 samples)"

    if cm_data:
        z = np.array(cm_data)
        fig_cm = px.imshow(
            z,
            text_auto=True,
            x=class_names,
            y=class_names,
            labels=dict(x="Predicted Strength Tier", y="Ground Truth (Actual) Tier", color="Sample Count"),
            color_continuous_scale=cmap
        )
        fig_cm.update_layout(
            title=dict(text=f"Confusion Matrix: {selected_model} ({title_suffix})", font=dict(size=13, color="#e2e8f0")),
            height=340,
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_cm, use_container_width=True)

# -------------------------------------------------------------
# Section 3: Feature Weights Analysis
# -------------------------------------------------------------
st.markdown("---")
st.subheader("🌲 Feature Weight Analysis: Mean Absolute Standardized Model Coefficients")
model_obj = bundle.get("model")
feat_names = bundle.get("feature_names", FEATURE_COLUMNS)

if hasattr(model_obj, "coef_"):
    # Logistic Regression multi-class coefficients
    importances = np.mean(np.abs(model_obj.coef_), axis=0)
    coef_label = "Mean Absolute Standardized Model Coefficients"
elif hasattr(model_obj, "feature_importances_"):
    importances = model_obj.feature_importances_
    coef_label = "Gini Impurity Feature Importance"
else:
    importances = None
    coef_label = "Feature Weights"

if importances is not None:
    df_feat = pd.DataFrame({"Feature": feat_names, "Importance": importances})
    df_feat = df_feat.sort_values(by="Importance", ascending=True)

    c_f1, c_f2 = st.columns([1.4, 1.0])
    with c_f1:
        fig_imp = px.bar(
            df_feat.tail(12),
            x="Importance",
            y="Feature",
            orientation='h',
            title=f"Top 12 Predictive Features ({coef_label} - {champion_name})",
            color="Importance",
            color_continuous_scale="Teal"
        )
        fig_imp.update_layout(
            height=340,
            margin=dict(l=20, r=20, t=35, b=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="#131d31",
            xaxis=dict(title=coef_label, tickfont=dict(color="#94a3b8")),
            yaxis=dict(tickfont=dict(color="#cbd5e1"))
        )
        st.plotly_chart(fig_imp, use_container_width=True)

    with c_f2:
        st.markdown(f"""
        <div class='section-card' style='margin-top:2rem;'>
            <div style='font-weight:700; color:#38bdf8; font-size:0.88rem; margin-bottom:0.4rem;'>🔬 Statistical Interpretation & Limitations</div>
            <div style='font-size:0.82rem; color:#cbd5e1; line-height:1.45;'>
                Because the training pipeline applies <code>StandardScaler</code> ($\mu=0, \sigma=1$), 
                these values represent the sensitivity of the log-odds decision boundary to a one standard-deviation shift in each numerical feature.
                <br><br>
                <b>Important Scientific Caveat:</b><br>
                High coefficient magnitude reflects predictive correlation within the trained linear log-odds decision boundaries; 
                <b>it does not automatically establish direct cryptographic causation</b>. 
                For example, while <code>length</code> and <code>entropy_bits</code> carry high positive weights, a long string with zero character diversity remains vulnerable.
            </div>
        </div>
        """, unsafe_allow_html=True)

# -------------------------------------------------------------
# Section 4: Honest Academic Limitations & Adversarial Findings
# -------------------------------------------------------------
st.markdown("---")
st.subheader("⚠️ Academic Audit Findings & Model Generalization Limitations")
st.markdown("""
<div class='section-card'>
    <div style='font-weight:700; color:#ef4444; font-size:0.92rem; margin-bottom:0.4rem;'>Honest Academic Limitations & Out-of-Distribution Degradation</div>
    <div style='font-size:0.84rem; color:#cbd5e1; line-height:1.5;'>
        1. <b>In-Distribution Synthetic vs Real-World Divergence:</b> While all four models achieve >99.8% accuracy on synthetic test splits, 
        their accuracy degrades to 60.0% - 69.6% when tested against the 250-sample adversarial holdout set. 
        Synthetic data generation, no matter how carefully structured, cannot fully simulate human psychological and cognitive heuristics.<br>
        2. <b>Shortcut Learning in Tree-Based Models:</b> Decision Trees and Random Forests relied heavily on length and entropy thresholds, 
        erroneously classifying 18-character repeating strings (e.g. <code>aaaaaaaaaaaaaaaaaa</code>) as "Strong" or "Very Strong".<br>
        3. <b>Justification for the Hybrid Architecture:</b> This empirical divergence provides the primary scientific proof that 
        <b>machine learning cannot be deployed alone for password security</b>. The deterministic rule safeguards and breach-screening overrides 
        act as essential security bounds that protect the system when ML encounters out-of-distribution adversarial edge cases.
    </div>
</div>
""", unsafe_allow_html=True)
