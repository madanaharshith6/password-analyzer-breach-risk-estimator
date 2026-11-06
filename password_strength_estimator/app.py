"""
Main Streamlit Application - Home Page
Project: A Rule-and-ML Hybrid Strength Estimator-Based Approach to Password Strength and Breach-Risk Estimation
Student: MADANA KOMAL SIVA SAI HARSHITH (Roll No: 24ME5A5408)
"""

import sys
from pathlib import Path
import streamlit as st

# Setup paths
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from config import STRENGTH_LABELS, STRENGTH_COLORS, BREACH_RISK_LEVELS

# Streamlit Page Configuration
st.set_page_config(
    page_title="Hybrid Password & Breach-Risk Estimator",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Unified Global Cybersecurity Dark Styling
st.markdown("""
<style>
    /* Global Base */
    .stApp {
        background-color: #0b1120;
        color: #f1f5f9;
    }
    
    /* Headers */
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #38bdf8;
        text-align: center;
        letter-spacing: -0.02em;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #94a3b8;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .academic-badge-bar {
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .academic-chip {
        display: inline-block;
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 9999px;
        padding: 0.3rem 0.9rem;
        font-size: 0.82rem;
        color: #38bdf8;
        margin: 0.2rem 0.4rem;
        font-weight: 600;
    }

    /* Metric Cards */
    .metric-card {
        background: #131d31;
        border: 1px solid #1e293b;
        border-top: 3px solid #0284c7;
        border-radius: 10px;
        padding: 1.1rem;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
        margin-bottom: 0.8rem;
    }
    .metric-title {
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #94a3b8;
        margin-bottom: 0.3rem;
        font-weight: 600;
    }
    .metric-value {
        font-size: 1.55rem;
        font-weight: 700;
        color: #f8fafc;
    }
    .metric-subtitle {
        color: #64748b;
        font-size: 0.78rem;
        margin-top: 0.2rem;
    }

    /* Architectural Container */
    .arch-flow-box {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 10px;
        padding: 1.2rem;
        margin-top: 0.5rem;
    }
    .arch-step {
        background: #1e293b;
        border-left: 3px solid #38bdf8;
        border-radius: 6px;
        padding: 0.7rem 0.9rem;
        margin-bottom: 0.6rem;
    }
    .arch-step-title {
        font-size: 0.85rem;
        font-weight: 700;
        color: #e2e8f0;
    }
    .arch-step-desc {
        font-size: 0.78rem;
        color: #94a3b8;
        margin-top: 0.15rem;
    }
</style>
""", unsafe_allow_html=True)

# Header Section
st.markdown("<div class='main-header'>🛡️ A Rule-and-ML Hybrid Strength Estimator</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>A Hybrid Approach to Password Strength and Breach-Risk Estimation</div>", unsafe_allow_html=True)

# Academic Attribution Bar
st.markdown("""
<div class='academic-badge-bar'>
    <span class='academic-chip'>🎓 B.Tech Mini-Project</span>
    <span class='academic-chip'>👤 Student: <b>MADANA KOMAL SIVA SAI HARSHITH</b></span>
    <span class='academic-chip'>🆔 Roll No: <b>24ME5A5408</b></span>
    <span class='academic-chip'>⚡ Python • Scikit-learn • Streamlit • SQLite</span>
</div>
""", unsafe_allow_html=True)

# Overview Banner
st.info(
    "💡 **Academic Research Focus:** This system addresses the dual blind-spots of traditional password meters: "
    "structural heuristic overconfidence (e.g., dictionary substitutions) and ignorance of compromised credential databases. "
    "It synthesizes a **deterministic rule engine**, **supervised machine learning**, and a **privacy-preserving k-anonymity breach verification layer**."
)

# Key Project Highlights (4 KPIs)
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("""
    <div class='metric-card' style='border-top-color: #38bdf8;'>
        <div class='metric-title'>Hybrid Synthesis</div>
        <div class='metric-value'>Rules + ML</div>
        <div class='metric-subtitle'>45% Heuristics + 55% ML Probabilities</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class='metric-card' style='border-top-color: #4ade80;'>
        <div class='metric-title'>ML Architecture</div>
        <div class='metric-value'>20 Features</div>
        <div class='metric-subtitle'>Supervised Classifier (Logistic Regression)</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class='metric-card' style='border-top-color: #f87171;'>
        <div class='metric-title'>Breach Detection</div>
        <div class='metric-value'>k-Anonymity</div>
        <div class='metric-subtitle'>SHA-1 Prefix Lookup (0 Plaintext Leakage)</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class='metric-card' style='border-top-color: #fbbf24;'>
        <div class='metric-title'>Standard Alignment</div>
        <div class='metric-value'>NIST 800-63B</div>
        <div class='metric-subtitle'>Zero Plaintext Storage • Dynamic Safeguards</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Main Content Columns
left_col, right_col = st.columns([1.2, 1.0])

with left_col:
    st.subheader("🎯 Project Abstract & Core Motivation")
    st.write(
        """
        Conventional password meters (such as basic length/character calculators or static heuristics) 
        suffer from two fundamental vulnerabilities:
        
        1. **Heuristic Bias & False Confidence:** Passwords such as `P@ssw0rd2024!` frequently receive inflated "Strong" 
        ratings based solely on length and character diversity, despite being standard targets in dictionary mutation attacks.
        2. **Breach Ignorance:** Traditional strength meters never cross-reference passwords against known compromise repositories, 
        permitting users to select credentials that have already been exposed in public database leaks.
        
        **The Proposed Hybrid Approach:**
        This academic project implements a three-tier defense architecture:
        - **Deterministic Rule Engine:** Computes Shannon entropy, character distribution, repetitive run penalties, 
        and detects sequential patterns (alphabetical, numerical, keyboard walks).
        - **Supervised Machine Learning:** Extracts a 20-dimensional numerical feature vector without storing plaintext, 
        classifying passwords into five ground-truth tiers (*Very Weak* to *Very Strong*).
        - **Compromise Override Safeguard:** Leverages local high-frequency dumps and remote **SHA-1 k-anonymity** queries 
        to immediately demote any breached credential to *Very Weak*, enforcing the Security Weakest-Link Principle.
        """
    )

    st.subheader("📌 Academic Project Objectives")
    st.markdown("""
    - **Zero-Plaintext Feature Extraction:** Design and implement a 20-dimensional numerical representation of password morphology.
    - **Multi-Model Empirical Comparison:** Train and evaluate Logistic Regression, Decision Tree, Random Forest, and SVM architectures on standard and out-of-distribution adversarial holdouts.
    - **Adaptive Hybrid Arbitration:** Synthesize heuristic scores with ML class expectation values, subject to hard cybersecurity safeguard overrides.
    - **Privacy-Preserving Audit Trail:** Record evaluation metadata in a local SQLite database without storing plaintext passwords or reversible artifacts.
    """)

with right_col:
    st.subheader("🗺️ System Architecture Workflow")
    st.markdown("""
    <div class='arch-flow-box'>
        <div class='arch-step'>
            <div class='arch-step-title'>1. In-Memory Ingestion</div>
            <div class='arch-step-desc'>Candidate password is ingested temporarily into volatile memory; zero disk logging.</div>
        </div>
        <div class='arch-step'>
            <div class='arch-step-title'>2. Parallel Tri-Stream Analysis</div>
            <div class='arch-step-desc'>
                • <b>Stream A:</b> Deterministic Heuristic Scoring (0-100 scale)<br>
                • <b>Stream B:</b> 20-Dimensional Numerical Feature Extraction & ML Inference<br>
                • <b>Stream C:</b> SHA-1 Prefix (5 hex chars) k-Anonymity Breach Verification
            </div>
        </div>
        <div class='arch-step'>
            <div class='arch-step-title'>3. Safeguard Enforcement & Weakest-Link Check</div>
            <div class='arch-step-desc'>If breached, monotonous, or length &lt; 8, hard overrides cap rating at <i>Very Weak</i> or <i>Weak</i>.</div>
        </div>
        <div class='arch-step'>
            <div class='arch-step-title'>4. Weighted Hybrid Synthesis</div>
            <div class='arch-step-desc'>Uncompromised credentials receive 45% Rule + 55% ML probability expectation.</div>
        </div>
        <div class='arch-step'>
            <div class='arch-step-title'>5. Actionable Remediation Guidance</div>
            <div class='arch-step-desc'>NIST SP 800-63B aligned recommendations and optional metadata-only audit logging.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Sidebar Download Option for Complete Project ZIP
zip_candidate = BASE_DIR.parent / "password_strength_estimator.zip"
if zip_candidate.exists():
    with open(zip_candidate, "rb") as f:
        zip_bytes = f.read()
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📦 Project Archive")
    st.sidebar.download_button(
        label="⬇️ Download Project (.zip)",
        data=zip_bytes,
        file_name="password_strength_estimator.zip",
        mime="application/zip",
        use_container_width=True,
        help="Download the complete verified project directory as a clean .zip archive."
    )

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #64748b; font-size: 0.82rem;'>"
    "🛡️ <b>Academic B.Tech Project</b> • Student: <b>MADANA KOMAL SIVA SAI HARSHITH</b> (Roll No: <b>24ME5A5408</b>)<br>"
    "Department of Mechanical Engineering / Computer Science & Cybersecurity • Python 3.11 • Streamlit • Scikit-Learn"
    "</div>",
    unsafe_allow_html=True
)
