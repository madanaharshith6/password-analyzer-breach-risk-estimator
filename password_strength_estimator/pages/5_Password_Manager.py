"""
Page 5: Password Manager & Secure Credential Vault
Instant-Response Local Password Manager with Indexed Search, CRUD, and Cached Security Metrics.
Optimized for Sub-Second Navigation and Zero Unnecessary Startup Overhead.
Student: MADANA KOMAL SIVA SAI HARSHITH (Roll No: 24ME5A5408)
"""

import sys
import time
from pathlib import Path
import streamlit as st

# Setup paths
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from config import STRENGTH_COLORS
from database.vault import VaultManager

# Page configuration
st.set_page_config(page_title="Password Manager • Secure Vault", page_icon="🔐", layout="wide")

# Theme Styling
st.markdown("""
<style>
    .page-title {
        font-size: 2rem;
        font-weight: 800;
        color: #38bdf8;
        margin-bottom: 0.2rem;
    }
    .vault-card {
        background-color: #131d31;
        border: 1px solid #1e293b;
        border-radius: 8px;
        padding: 0.9rem 1.1rem;
        margin-bottom: 0.6rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .service-badge {
        font-size: 1rem;
        font-weight: 700;
        color: #f8fafc;
    }
    .meta-text {
        font-size: 0.8rem;
        color: #94a3b8;
    }
    .kpi-box {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 8px;
        padding: 0.8rem;
        text-align: center;
    }
    .kpi-val {
        font-size: 1.4rem;
        font-weight: 700;
        color: #38bdf8;
    }
    .kpi-lbl {
        font-size: 0.75rem;
        color: #94a3b8;
        text-transform: uppercase;
    }
</style>
""", unsafe_allow_html=True)

# Instant Render: Top Header & Timing Marker
t_render_start = time.perf_counter()

st.markdown("<div class='page-title'>🔐 Secure Password Manager & Credential Vault</div>", unsafe_allow_html=True)
st.caption(
    "High-performance local credential vault with instant indexed search, encrypted local persistence, "
    "and zero startup latency."
)

# Cached Database Manager Singleton (Connection Pooling)
@st.cache_resource
def get_vault_manager():
    return VaultManager()

vault_manager = get_vault_manager()

# -------------------------------------------------------------
# Top Controls & Quick Metrics
# -------------------------------------------------------------
col_search, col_filter, col_act = st.columns([2.0, 1.2, 1.0])

with col_search:
    search_query = st.text_input(
        "🔍 Search Credentials:",
        placeholder="Type service name (e.g. GitHub, Google) or username...",
        label_visibility="collapsed"
    )

with col_filter:
    filter_tier = st.selectbox(
        "Filter by Strength:",
        options=["All Tiers", "Very Weak / Weak", "Moderate", "Strong / Very Strong"],
        label_visibility="collapsed"
    )

with col_act:
    show_passwords_global = st.checkbox("👁️ Reveal Passwords", value=False)

# Fetch matching records via indexed query
total_records = vault_manager.count_entries()
filtered_records = vault_manager.get_entries(search_query=search_query, limit=100)

# Apply strength tier filter in-memory (instantaneous)
if filter_tier == "Very Weak / Weak":
    display_records = [r for r in filtered_records if r["strength_tier"] in ("Very Weak", "Weak")]
elif filter_tier == "Moderate":
    display_records = [r for r in filtered_records if r["strength_tier"] == "Moderate"]
elif filter_tier == "Strong / Very Strong":
    display_records = [r for r in filtered_records if r["strength_tier"] in ("Strong", "Very Strong")]
else:
    display_records = filtered_records

# Quick Telemetry Header
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f"""
    <div class='kpi-box'>
        <div class='kpi-lbl'>Total Vault Entries</div>
        <div class='kpi-val'>{total_records}</div>
    </div>
    """, unsafe_allow_html=True)

weak_count = sum(1 for r in filtered_records if r["strength_tier"] in ("Very Weak", "Weak"))
with k2:
    st.markdown(f"""
    <div class='kpi-box' style='border-top: 2px solid #ef4444;'>
        <div class='kpi-lbl'>Weak / Vulnerable</div>
        <div class='kpi-val' style='color:#ef4444;'>{weak_count}</div>
    </div>
    """, unsafe_allow_html=True)

strong_count = sum(1 for r in filtered_records if r["strength_tier"] in ("Strong", "Very Strong"))
with k3:
    st.markdown(f"""
    <div class='kpi-box' style='border-top: 2px solid #4ade80;'>
        <div class='kpi-lbl'>Resilient Credentials</div>
        <div class='kpi-val' style='color:#4ade80;'>{strong_count}</div>
    </div>
    """, unsafe_allow_html=True)

render_latency_ms = (time.perf_counter() - t_render_start) * 1000
with k4:
    st.markdown(f"""
    <div class='kpi-box' style='border-top: 2px solid #38bdf8;'>
        <div class='kpi-lbl'>Page Render Latency</div>
        <div class='kpi-val' style='color:#38bdf8;'>{render_latency_ms:.1f} ms</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# -------------------------------------------------------------
# Collapsible "Add New Credential" Form
# -------------------------------------------------------------
with st.expander("➕ Add New Credential to Vault", expanded=False):
    with st.form(key="add_credential_form", clear_on_submit=True):
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            service_input = st.text_input("Service / Application Name:", placeholder="e.g. GitHub, Google, AWS, LinkedIn")
            username_input = st.text_input("Username or Email Address:", placeholder="e.g. student@university.edu")
        with f_col2:
            password_input = st.text_input("Password:", type="password", placeholder="Enter credential password...")
            eval_security = st.checkbox("Run Lightweight Strength Audit on Save", value=True)

        submitted = st.form_submit_button("💾 Save Credential to Vault", type="primary", use_container_width=True)

        if submitted:
            if not service_input.strip() or not username_input.strip() or not password_input:
                st.error("⚠️ All fields (Service Name, Username, and Password) are required.")
            else:
                tier = "Moderate"
                score = 50.0

                # Lightweight evaluation without loading heavy ML pipeline
                if eval_security:
                    try:
                        from modules.password_rules import PasswordRuleEngine
                        rule_engine = PasswordRuleEngine()
                        eval_res = rule_engine.evaluate(password_input)
                        tier = eval_res["category"]
                        score = eval_res["score"]
                    except Exception:
                        pass

                entry_id = vault_manager.add_entry(
                    service_name=service_input,
                    username=username_input,
                    password_val=password_input,
                    strength_tier=tier,
                    strength_score=score
                )
                st.success(f"✅ Credential for **{service_input}** saved successfully!")
                st.rerun()

# -------------------------------------------------------------
# Saved Credentials List View
# -------------------------------------------------------------
st.subheader(f"📋 Stored Vault Records ({len(display_records)} matching)")

if not display_records:
    if search_query:
        st.info(f"No credentials found matching '{search_query}'. Try a different search term or add an entry above.")
    else:
        st.info("Your vault is currently empty. Click '➕ Add New Credential to Vault' above to store your first login.")
else:
    for item in display_records:
        e_id = item["entry_id"]
        tier_color = STRENGTH_COLORS.get(item["strength_tier"], "#94a3b8")
        masked_pwd = item["password_val"] if show_passwords_global else "••••••••••••"

        with st.container():
            c_info, c_pwd, c_tier, c_action = st.columns([1.5, 1.5, 1.1, 0.9])

            with c_info:
                st.markdown(f"<div class='service-badge'>{item['service_name']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='meta-text'>👤 {item['username']}</div>", unsafe_allow_html=True)

            with c_pwd:
                st.code(masked_pwd, language=None)
                st.caption(f"Last updated: {item['updated_at']}")

            with c_tier:
                st.markdown(f"""
                <div style='margin-top:0.4rem;'>
                    <span style='background:rgba(255,255,255,0.07); border:1px solid {tier_color}; color:{tier_color}; padding:0.25rem 0.6rem; border-radius:9999px; font-size:0.8rem; font-weight:600;'>
                        {item['strength_tier']} ({item['strength_score']:.0f})
                    </span>
                </div>
                """, unsafe_allow_html=True)

            with c_action:
                st.markdown("<div style='margin-top:0.3rem;'></div>", unsafe_allow_html=True)
                btn_del = st.button("🗑️ Delete", key=f"del_{e_id}", use_container_width=True)
                if btn_del:
                    vault_manager.delete_entry(e_id)
                    st.toast(f"Deleted {item['service_name']} record.", icon="🗑️")
                    st.rerun()

st.markdown("---")
st.caption(
    "🔒 **Vault Privacy Architecture:** Passwords are stored in your private local SQLite database (`password_audit.db`). "
    "Credentials are never transmitted to external servers, cloud storage, or application logs."
)
