"""
Page 1: Password Analyzer
Interactive Real-Time Password Strength and Breach-Risk Estimation Console
Academic Project: A Rule-and-ML Hybrid Strength Estimator
Student: MADANA KOMAL SIVA SAI HARSHITH (Roll No: 24ME5A5408)
"""

import sys
from pathlib import Path
import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# Setup paths
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from modules.hybrid_engine import HybridStrengthEngine
from database.history import AuditHistoryManager
from config import STRENGTH_COLORS, BREACH_RISK_LEVELS

# Streamlit Page Config
st.set_page_config(page_title="Password Analyzer • Hybrid Estimator", page_icon="🔍", layout="wide")

# Custom Styling
st.markdown("""
<style>
    .page-title {
        font-size: 2rem;
        font-weight: 800;
        color: #38bdf8;
        margin-bottom: 0.2rem;
    }
    .metric-box {
        background-color: #131d31;
        border: 1px solid #1e293b;
        border-radius: 8px;
        padding: 0.9rem;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.25);
    }
    .metric-val {
        font-size: 1.45rem;
        font-weight: 700;
        margin: 0.2rem 0;
    }
    .metric-sub {
        font-size: 0.78rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-detail {
        font-size: 0.8rem;
        color: #cbd5e1;
    }
    .section-card {
        background-color: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 8px;
        padding: 1.1rem;
        margin-bottom: 1rem;
    }
    .weakness-tag {
        background: rgba(239, 68, 68, 0.15);
        border-left: 3px solid #ef4444;
        padding: 0.45rem 0.75rem;
        border-radius: 4px;
        margin-bottom: 0.4rem;
        font-size: 0.85rem;
        color: #fca5a5;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='page-title'>🔍 Password Analyzer & Breach Risk Estimator</div>", unsafe_allow_html=True)
st.caption(
    "Evaluate candidate credentials using a deterministic heuristic rule engine, "
    "a 20-feature supervised machine learning model, and real-time SHA-1 k-anonymity breach screening."
)

# Lazy-Loaded Cached Resource Singletons
@st.cache_resource(show_spinner=False)
def get_hybrid_engine():
    from modules.hybrid_engine import HybridStrengthEngine
    return HybridStrengthEngine()

@st.cache_resource(show_spinner=False)
def get_audit_manager():
    return AuditHistoryManager()

# Input Configuration Form
st.markdown("---")
with st.container():
    col_input, col_ctrl = st.columns([2.6, 1.2])

    with col_ctrl:
        st.markdown("<div style='font-size:0.85rem; font-weight:600; color:#94a3b8; margin-bottom:0.4rem;'>EVALUATION SETTINGS</div>", unsafe_allow_html=True)
        show_password = st.checkbox(
            "👁️ Unmask Password",
            value=False,
            help="Toggle to view characters in plaintext for visual confirmation."
        )
        auto_audit = st.checkbox(
            "💾 Record Anonymized Audit Log",
            value=False,
            help="Opt-in: Persists only mathematical score metrics, timestamps, and length buckets to local SQLite. Plaintext passwords and hashes are NEVER stored."
        )

    with col_input:
        input_type = "default" if show_password else "password"
        user_password = st.text_input(
            "Candidate Password to Evaluate:",
            type=input_type,
            placeholder="Enter password to evaluate (e.g., Tr0ub4dor&3, correct-horse-battery-staple)",
            help="Privacy guarantee: The password is processed strictly in volatile memory and is never written to disk or logs."
        )

    analyze_clicked = st.button("🚀 Analyze Password", type="primary", use_container_width=True)

# Trigger Analysis Execution
if analyze_clicked:
    if not user_password.strip():
        st.warning("⚠️ **Input Required:** Please enter a candidate password into the field above before running analysis.")
        if "last_results" in st.session_state:
            del st.session_state["last_results"]
    else:
        with st.spinner("Executing rule heuristics, extracting 20 features, invoking ML classifier, and screening breach repositories..."):
            hybrid_engine = get_hybrid_engine()
            results = hybrid_engine.analyze(user_password)
            st.session_state["last_results"] = results
            st.session_state["evaluated_len"] = len(user_password)

            # Opt-in Audit Logging
            if auto_audit:
                audit_manager = get_audit_manager()
                audit_manager.record_analysis(
                    strength_category=results["hybrid_category"],
                    rule_score=results["rule_based_score"],
                    ml_prediction=results["ml_prediction_label"],
                    breach_risk_category=results["breach_assessment"]["risk_tier"],
                    entropy_score=results["features"]["entropy_bits"],
                    password_length=len(user_password)
                )
                st.session_state["audit_logged"] = True
            else:
                st.session_state["audit_logged"] = False

# Render Results
if "last_results" in st.session_state:
    results = st.session_state["last_results"]
    st.markdown("---")

    # Safeguard Warning Banner (if activated)
    if results.get("safeguard_override"):
        st.error(
            f"🚨 **CYBERSECURITY SAFEGUARD OVERRIDE ACTIVATED:** {results['safeguard_reason']}. "
            "Although this candidate credential may contain diverse character sets or pass superficial checks, "
            "it is fundamentally vulnerable. The Hybrid Arbitration Engine has capped the rating to prevent false security confidence."
        )

    if st.session_state.get("audit_logged"):
        st.toast("✅ Anonymized evaluation metadata saved to local SQLite audit log.", icon="💾")

    # ---------------------------------------------------------
    # Core Summary Metric Cards (Sections 1, 2, 3, 4)
    # ---------------------------------------------------------
    m1, m2, m3, m4 = st.columns(4)
    cat_color = results["hybrid_color"]

    with m1:
        st.markdown(f"""
        <div class='metric-box' style='border-top: 3px solid {cat_color};'>
            <div class='metric-sub'>1. HYBRID CLASSIFICATION</div>
            <div class='metric-val' style='color: {cat_color};'>{results["hybrid_category"]}</div>
            <div class='metric-detail'>Composite Score: <b>{results["hybrid_score"]:.1f} / 100</b></div>
        </div>
        """, unsafe_allow_html=True)

    with m2:
        st.markdown(f"""
        <div class='metric-box' style='border-top: 3px solid #38bdf8;'>
            <div class='metric-sub'>2. RULE-BASED ENGINE</div>
            <div class='metric-val' style='color: #38bdf8;'>{results["rule_based_category"]}</div>
            <div class='metric-detail'>Heuristic Score: <b>{results["rule_based_score"]:.1f} / 100</b></div>
        </div>
        """, unsafe_allow_html=True)

    with m3:
        st.markdown(f"""
        <div class='metric-box' style='border-top: 3px solid #4ade80;'>
            <div class='metric-sub'>3. MACHINE LEARNING</div>
            <div class='metric-val' style='color: #4ade80;'>{results["ml_prediction_label"]}</div>
            <div class='metric-detail'><b>{results.get("ml_model_name", "Logistic Regression")}</b> ({results["ml_confidence"]*100:.1f}% conf)</div>
        </div>
        """, unsafe_allow_html=True)

    breach_info = results["breach_assessment"]
    with m4:
        st.markdown(f"""
        <div class='metric-box' style='border-top: 3px solid {breach_info["risk_color"]};'>
            <div class='metric-sub'>4. BREACH-RISK STATUS</div>
            <div class='metric-val' style='color: {breach_info["risk_color"]};'>{breach_info["risk_tier"]}</div>
            <div class='metric-detail'>Breach Count: <b>{breach_info["breach_count"]:,}</b></div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # Visualizations: Strength Gauge & Feature Radar
    # ---------------------------------------------------------
    col_gauge, col_radar = st.columns([1.1, 1.1])

    with col_gauge:
        st.markdown("<div style='font-size:1rem; font-weight:700; color:#e2e8f0;'>⚡ Hybrid Strength Gauge</div>", unsafe_allow_html=True)
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=results["hybrid_score"],
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': f"{results['hybrid_category']} (Score {results['hybrid_score']:.1f})", 'font': {'size': 15, 'color': cat_color}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#94a3b8"},
                'bar': {'color': cat_color},
                'bgcolor': "#131d31",
                'borderwidth': 1,
                'bordercolor': "#334155",
                'steps': [
                    {'range': [0, 25], 'color': 'rgba(239, 68, 68, 0.20)'},
                    {'range': [25, 45], 'color': 'rgba(249, 115, 22, 0.20)'},
                    {'range': [45, 65], 'color': 'rgba(245, 158, 11, 0.20)'},
                    {'range': [65, 85], 'color': 'rgba(74, 222, 128, 0.20)'},
                    {'range': [85, 100], 'color': 'rgba(34, 197, 94, 0.28)'}
                ],
                'threshold': {
                    'line': {'color': "#ffffff", 'width': 3},
                    'thickness': 0.75,
                    'value': results["hybrid_score"]
                }
            }
        ))
        fig_gauge.update_layout(height=260, margin=dict(l=20, r=20, t=30, b=20), paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_gauge, use_container_width=True)

        st.caption(
            f"⏱️ **Theoretical Offline Crack Time:** `{results['rule_details']['crack_time']}` "
            f"at 100 Billion guesses/sec (Effective Entropy: `{results['features']['entropy_bits']:.1f}` bits)."
        )

    with col_radar:
        st.markdown("<div style='font-size:1rem; font-weight:700; color:#e2e8f0;'>📊 5. Password Morphological Characteristics</div>", unsafe_allow_html=True)
        features = results["features"]
        categories = ["Length (Scaled)", "Char Variety", "Shannon Entropy", "Search Space Bits", "Unique Char Ratio"]
        vals = [
            min(100.0, features["length"] * 5.0),
            features["char_variety"] * 25.0,
            min(100.0, features["shannon_entropy"] * 25.0),
            min(100.0, features["entropy_bits"] * 0.8),
            features["unique_char_ratio"] * 100.0
        ]

        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=vals,
            theta=categories,
            fill='toself',
            fillcolor='rgba(56, 189, 248, 0.25)',
            line=dict(color='#38bdf8', width=2),
            name='Normalized Metric'
        ))
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=8, color="#94a3b8")),
                bgcolor="#131d31"
            ),
            height=260,
            margin=dict(l=30, r=30, t=25, b=20),
            paper_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    # ---------------------------------------------------------
    # Granular Breakdown: Characteristics & Rule Details
    # ---------------------------------------------------------
    st.markdown("---")
    rule_det = results["rule_details"]
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("<div style='font-weight:600; color:#38bdf8; margin-bottom:0.3rem;'>Character Composition</div>", unsafe_allow_html=True)
        st.write(f"• **Length:** {rule_det['length']} characters")
        st.write(f"• **Uppercase:** {rule_det['uppercase_count']}")
        st.write(f"• **Lowercase:** {rule_det['lowercase_count']}")
        st.write(f"• **Digits:** {rule_det['digits_count']}")
        st.write(f"• **Special Characters:** {rule_det['special_count']}")

    with c2:
        st.markdown("<div style='font-weight:600; color:#38bdf8; margin-bottom:0.3rem;'>Entropy & Search Space</div>", unsafe_allow_html=True)
        st.write(f"• **Shannon Entropy:** {rule_det['shannon_entropy']} bits/char")
        st.write(f"• **Active Character Pool ($R$):** {results['features']['pool_size']:.0f} chars")
        st.write(f"• **Combinatorial Entropy:** {rule_det['total_entropy_bits']} bits")
        st.write(f"• **Unique Ratio:** {results['features']['unique_char_ratio']*100:.1f}%")
        st.write(f"• **Max Repeated Run:** {rule_det['max_consecutive_repeated']} identical")

    with c3:
        st.markdown("<div style='font-weight:600; color:#38bdf8; margin-bottom:0.3rem;'>Pattern Identifiers</div>", unsafe_allow_html=True)
        st.write(f"• **Alphabetical Sequence:** {'🔴 Detected' if rule_det['has_alphabetical_sequence'] else '🟢 None'}")
        st.write(f"• **Numerical Sequence:** {'🔴 Detected' if rule_det['has_numerical_sequence'] else '🟢 None'}")
        st.write(f"• **Keyboard Walk:** {'🔴 Detected' if rule_det['has_keyboard_sequence'] else '🟢 None'}")
        st.write(f"• **Dictionary Roots:** {', '.join(rule_det['dictionary_matches']) if rule_det['dictionary_matches'] else '🟢 None'}")
        st.write(f"• **Breach Source:** `{breach_info['detection_source']}`")

    # ---------------------------------------------------------
    # Sections 6 & 7: Weaknesses vs Recommendations
    # ---------------------------------------------------------
    st.markdown("---")
    col_weakness, col_guidance = st.columns([1.1, 1.1])

    with col_weakness:
        st.subheader("⚠️ 6. Identified Security Weaknesses")
        weaknesses = results.get("identified_weaknesses", [])
        if not weaknesses:
            st.success("🟢 No critical structural weaknesses or breach exposures detected.")
        else:
            for w in weaknesses:
                st.markdown(f"<div class='weakness-tag'>• {w}</div>", unsafe_allow_html=True)

        if rule_det["rules_passed"]:
            with st.expander("✅ Passed Structural Checks", expanded=False):
                for p_check in rule_det["rules_passed"]:
                    st.markdown(f"- 🟢 {p_check}")

    with col_guidance:
        st.subheader("🛡️ 7. Recommended Security Improvements")
        recs = results.get("recommendations", [])
        if not recs:
            st.info("No actionable improvements required. The credential demonstrates exceptional complexity.")
        else:
            for rec in recs:
                p = rec["priority"]
                if p == "CRITICAL":
                    icon, b_col = "🚨", "#ef4444"
                elif p == "HIGH":
                    icon, b_col = "⚠️", "#f97316"
                elif p == "MEDIUM":
                    icon, b_col = "💡", "#f59e0b"
                else:
                    icon, b_col = "ℹ️", "#3b82f6"

                st.markdown(f"""
                <div style='background-color: #131d31; border-left: 3px solid {b_col}; padding: 0.75rem 0.9rem; border-radius: 6px; margin-bottom: 0.5rem;'>
                    <div style='font-weight: 700; color: #f8fafc; font-size: 0.88rem;'>{icon} [{p}] {rec["title"]}</div>
                    <div style='font-size: 0.82rem; color: #94a3b8; margin-top: 0.2rem;'>{rec["description"]}</div>
                </div>
                """, unsafe_allow_html=True)

# -------------------------------------------------------------
# Section D: Privacy-Preserving Metadata-Only Audit History
# -------------------------------------------------------------
st.markdown("---")
with st.expander("📜 Privacy-Preserving Metadata-Only Audit History (SQLite Database)"):
    st.markdown(
        "**Privacy Architecture Specification:**\n"
        "This evaluation history strictly stores non-reversible operational telemetry: "
        "`Timestamp`, `Strength Category`, `Rule Score`, `ML Prediction Label`, `Breach Risk Tier`, "
        "`Theoretical Entropy (bits)`, and coarse `Length Bucket` (`<8 chars`, `8-11 chars`, `12-15 chars`, `>=16 chars`). "
        "**Plaintext passwords and cryptographic hashes are never saved to disk or application logs.**"
    )

    audit_manager = get_audit_manager()
    recent_records = audit_manager.get_recent(limit=25)
    if recent_records:
        df_history = pd.DataFrame(recent_records)
        df_display = df_history[["timestamp", "strength_category", "rule_score", "ml_prediction", "breach_risk_category", "entropy_score", "length_bucket"]]
        st.dataframe(df_display, use_container_width=True, hide_index=True)

        st.markdown("<br>", unsafe_allow_html=True)
        col_purge1, col_purge2 = st.columns([1.5, 1.0])
        with col_purge1:
            confirm_purge = st.checkbox("⚠️ Confirm permanent deletion of all local audit records", value=False)
        with col_purge2:
            if st.button("🗑️ Purge Historical Audit Log", disabled=not confirm_purge, type="secondary"):
                count = audit_manager.clear_all()
                st.success(f"Successfully purged {count} audit records from SQLite database.")
                st.rerun()
    else:
        st.info("Audit database is currently empty. Enable 'Record Anonymized Audit Log' during password analysis to log metadata.")
