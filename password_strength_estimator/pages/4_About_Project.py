"""
Page 4: About Project & Academic Viva Defense Documentation
Comprehensive B.Tech Project Report, Mathematical Formulations, Architecture, and Viva FAQs
Student: MADANA KOMAL SIVA SAI HARSHITH (Roll No: 24ME5A5408)
"""

import sys
from pathlib import Path
import streamlit as st
import pandas as pd

# Setup paths
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

st.set_page_config(page_title="About Project • Academic Defense", page_icon="📖", layout="wide")

st.markdown("""
<style>
    .page-title {
        font-size: 2rem;
        font-weight: 800;
        color: #38bdf8;
        margin-bottom: 0.2rem;
    }
    .doc-card {
        background-color: #131d31;
        border: 1px solid #1e293b;
        border-radius: 8px;
        padding: 1.1rem;
        margin-bottom: 1.1rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    .viva-box {
        background-color: #0f172a;
        border-left: 3px solid #38bdf8;
        border-radius: 6px;
        padding: 0.85rem 1rem;
        margin-bottom: 0.8rem;
    }
    .viva-q {
        font-weight: 700;
        color: #f1f5f9;
        font-size: 0.92rem;
        margin-bottom: 0.25rem;
    }
    .viva-a {
        color: #94a3b8;
        font-size: 0.84rem;
        line-height: 1.5;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='page-title'>📖 Academic Project Documentation & Defense Dossier</div>", unsafe_allow_html=True)
st.caption("A Rule-and-ML Hybrid Strength Estimator-Based Approach to Password Strength and Breach-Risk Estimation")

# Attribution Box
st.markdown("""
<div style='background:#1e293b; border:1px solid #334155; border-radius:6px; padding:0.6rem 1rem; margin-bottom:1rem; font-size:0.84rem; color:#cbd5e1;'>
    🎓 <b>Candidate:</b> MADANA KOMAL SIVA SAI HARSHITH &nbsp;|&nbsp; 
    🆔 <b>Roll Number:</b> 24ME5A5408 &nbsp;|&nbsp; 
    📚 <b>Degree:</b> B.Tech Mini-Project &nbsp;|&nbsp; 
    ⚡ <b>Domain:</b> Cybersecurity & Applied Machine Learning
</div>
""", unsafe_allow_html=True)

# Tabs
tab_abstract, tab_arch, tab_method, tab_defense = st.tabs([
    "📑 Abstract & Problem Statement",
    "🏛️ Existing vs Proposed System",
    "🔬 Methodology & Mathematics",
    "🎓 University Defense Viva Q&A"
])

# -------------------------------------------------------------
# Tab 1: Abstract & Problem Statement
# -------------------------------------------------------------
with tab_abstract:
    st.subheader("📑 Project Abstract")
    st.markdown("""
    <div class='doc-card'>
        <p style='color:#cbd5e1; line-height: 1.6;'>
        <b>Abstract:</b><br>
        User authentication remains the primary attack surface across networked applications. 
        Traditional password strength estimation systems predominantly depend on naive length thresholds, 
        arbitrary composition rules, or unweighted combinatorial search-space calculations. As an unintended consequence, 
        predictable passwords such as <code>P@ssw0rd2024!</code> frequently receive inflated "Strong" ratings despite being 
        primary targets in automated dictionary mutation and rule-based cracking attacks. Furthermore, conventional password 
        meters operate in isolation from compromised credential feeds, leaving users unaware when utilizing passwords that have 
        already been published in global breach databases.
        </p>
        <p style='color:#cbd5e1; line-height: 1.6;'>
        This project introduces a <b>Rule-and-ML Hybrid Password Strength and Breach-Risk Estimation Engine</b>. 
        The system extracts a 20-dimensional numerical feature vector capturing Shannon entropy, character diversity ratios, 
        repetition runs, and sequential structures (alphabetical, numerical, and keyboard walks) without persisting raw credentials. 
        Four supervised machine learning architectures—Logistic Regression, Decision Trees, Random Forests, and Support Vector Machines—are 
        empirically trained and compared across in-distribution test splits and an independent 250-sample out-of-distribution adversarial holdout dataset. 
        A dual-stream hybrid fusion engine synthesizes deterministic rule heuristics with ML class expectation probabilities, 
        governed by deterministic cybersecurity safeguard overrides and live <b>SHA-1 k-anonymity</b> breach screening.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("🎯 Problem Statement")
    st.markdown("""
    1. **Heuristic Bias and False Confidence:** Static composition rules fail to model structural predictability, rewarding mutated dictionary roots.
    2. **Disregard for Breach Intelligence:** Offline entropy calculations are invalid if the credential is already circulating in public credential dumps.
    3. **Privacy Vulnerabilities in Credential Evaluation:** Traditional online strength testers expose users to surveillance if plaintext credentials or reversible hashes are transmitted or logged.
    """)

# -------------------------------------------------------------
# Tab 2: Existing vs Proposed
# -------------------------------------------------------------
with tab_arch:
    st.subheader("🏛️ Architectural Comparison: Existing vs Proposed System")

    comp_table = [
        {
            "Architectural Dimension": "Evaluation Engine",
            "Existing Systems (Regex / zxcvbn)": "Single deterministic heuristic or static graph search",
            "Proposed Rule-and-ML Hybrid System": "Tri-stream: Heuristic Rules + Supervised ML + Breach Screening"
        },
        {
            "Architectural Dimension": "Feature Representation",
            "Existing Systems (Regex / zxcvbn)": "Raw character counts and basic spatial graph matching",
            "Proposed Rule-and-ML Hybrid System": "20-dimensional standardized numerical feature vector"
        },
        {
            "Architectural Dimension": "Breach Threat Awareness",
            "Existing Systems (Regex / zxcvbn)": "Completely blind to public credential dumps",
            "Proposed Rule-and-ML Hybrid System": "Dual-layer: Local top breached list + Live SHA-1 k-anonymity HIBP API"
        },
        {
            "Architectural Dimension": "Compromised Password Handling",
            "Existing Systems (Regex / zxcvbn)": "Can score breached passwords as 'Strong' if long",
            "Proposed Rule-and-ML Hybrid System": "Strict Override: Caps compromised credentials to 'Very Weak' immediately"
        },
        {
            "Architectural Dimension": "Out-of-Distribution Resilience",
            "Existing Systems (Regex / zxcvbn)": "Rule-based systems susceptible to unseen patterns",
            "Proposed Rule-and-ML Hybrid System": "Evaluated on 250-sample adversarial holdout with documented limitations"
        },
        {
            "Architectural Dimension": "Data Persistence & Privacy",
            "Existing Systems (Regex / zxcvbn)": "Varies; some online tools transmit plaintexts",
            "Proposed Rule-and-ML Hybrid System": "Zero plaintext storage; opt-in metadata-only SQLite audit history"
        }
    ]
    st.dataframe(pd.DataFrame(comp_table), use_container_width=True, hide_index=True)

    st.subheader("🛠️ Software Technology Stack")
    st.markdown("""
    - **Programming Language:** Python 3.11
    - **Web Framework & UI:** Streamlit (Wide Responsive Layout, Custom Theme, Plotly Visualizations)
    - **Machine Learning Library:** Scikit-learn (Logistic Regression, Decision Tree, Random Forest, LinearSVC)
    - **Scientific Computation:** NumPy, Pandas, Math
    - **Data Persistence:** SQLite with SQLAlchemy ORM (Privacy-preserving audit telemetry)
    - **Testing Harness:** Pytest (Unit, integration, and adversarial boundary test suite)
    - **Model Serialization:** Joblib
    """)

# -------------------------------------------------------------
# Tab 3: Methodology & Mathematics
# -------------------------------------------------------------
with tab_method:
    st.subheader("🔬 Methodology & Mathematical Formulations")
    st.write("All mathematical formulas are rendered directly via LaTeX.")

    st.markdown("#### 1. Shannon Information Entropy")
    st.write(
        "Shannon entropy measures the average information density per character in a candidate password string $s$ "
        "of length $L$, based on empirical character probabilities $p_i$:"
    )
    st.latex(r"H(s) = -\sum_{i=1}^{k} p_i \log_2(p_i) \quad \text{[bits / character]}")
    st.write("Where $k$ is the number of distinct characters in $s$, and $p_i = \text{count}(c_i) / L$.")

    st.markdown("---")
    st.markdown("#### 2. Combinatorial Keyspace Search Entropy")
    st.write(
        "Given an active character pool $R$ (where $R \in [1, 95]$ depending on lowercase, uppercase, digits, and symbols present):"
    )
    st.latex(r"E_{\text{theoretical}} = L \cdot \log_2(R) \quad \text{[total search space bits]}")
    st.write(
        "To account for non-uniform character distributions in repetitive strings, the effective keyspace entropy "
        "incorporates an empirical efficiency scalar $\eta$:"
    )
    st.latex(r"\eta = \min\left(1.0, \max\left(0.1, \frac{H(s)}{\log_2(R)}\right)\right), \quad E_{\text{eff}} = L \cdot \log_2(R) \cdot \eta")

    st.markdown("---")
    st.markdown("#### 3. Standardized 20-Dimensional Numerical Feature Vector ($\mathbf{x} \in \mathbb{R}^{20}$)")
    st.write(
        "The supervised machine learning model ingests exclusively numerical representations without storing or passing raw passwords. "
        "The 20 features in `modules/feature_extraction.py` are mapped as follows:"
    )

    feature_table_data = [
        {"#": 1, "Feature Name": "length", "Mathematical Formulation": "L = |s|", "Type": "Integer", "Security & ML Purpose": "Primary keyspace scaling factor"},
        {"#": 2, "Feature Name": "num_uppercase", "Mathematical Formulation": "N_{upper} = \\sum [c \\in A-Z]", "Type": "Integer", "Security & ML Purpose": "Uppercase character frequency count"},
        {"#": 3, "Feature Name": "num_lowercase", "Mathematical Formulation": "N_{lower} = \\sum [c \\in a-z]", "Type": "Integer", "Security & ML Purpose": "Lowercase character frequency count"},
        {"#": 4, "Feature Name": "num_digits", "Mathematical Formulation": "N_{digits} = \\sum [c \\in 0-9]", "Type": "Integer", "Security & ML Purpose": "Numeric digit frequency count"},
        {"#": 5, "Feature Name": "num_special", "Mathematical Formulation": "N_{special} = \\sum [c \\notin \\text{alnum}]", "Type": "Integer", "Security & ML Purpose": "Special symbol frequency count"},
        {"#": 6, "Feature Name": "ratio_uppercase", "Mathematical Formulation": "R_{upper} = N_{upper} / L", "Type": "Float [0,1]", "Security & ML Purpose": "Proportional uppercase distribution"},
        {"#": 7, "Feature Name": "ratio_lowercase", "Mathematical Formulation": "R_{lower} = N_{lower} / L", "Type": "Float [0,1]", "Security & ML Purpose": "Proportional lowercase distribution"},
        {"#": 8, "Feature Name": "ratio_digits", "Mathematical Formulation": "R_{digits} = N_{digits} / L", "Type": "Float [0,1]", "Security & ML Purpose": "Proportional numeric distribution"},
        {"#": 9, "Feature Name": "ratio_special", "Mathematical Formulation": "R_{special} = N_{special} / L", "Type": "Float [0,1]", "Security & ML Purpose": "Proportional special symbol distribution"},
        {"#": 10, "Feature Name": "char_variety", "Mathematical Formulation": "V = \\sum_{k} [N_k > 0]", "Type": "Integer [1,4]", "Security & ML Purpose": "Count of active character classes"},
        {"#": 11, "Feature Name": "unique_char_ratio", "Mathematical Formulation": "U = |\\text{set}(s)| / L", "Type": "Float [0,1]", "Security & ML Purpose": "Diversity penalty for repetitive characters"},
        {"#": 12, "Feature Name": "shannon_entropy", "Mathematical Formulation": "H(s) = -\\sum p_i \\log_2(p_i)", "Type": "Float [0,8]", "Security & ML Purpose": "Information uncertainty per character"},
        {"#": 13, "Feature Name": "max_consecutive_repeated", "Mathematical Formulation": "M_{repeat} = \\max(\\text{run}_i)", "Type": "Integer", "Security & ML Purpose": "Identifies monotonous runs (e.g. 'aaaa')"},
        {"#": 14, "Feature Name": "has_sequential_char", "Mathematical Formulation": "I_{alpha} \\in \\{0, 1\\}", "Type": "Binary", "Security & ML Purpose": "Detects alphabetical runs ('abc', 'xyz')"},
        {"#": 15, "Feature Name": "has_sequential_num", "Mathematical Formulation": "I_{num} \\in \\{0, 1\\}", "Type": "Binary", "Security & ML Purpose": "Detects numeric sequences ('123', '789')"},
        {"#": 16, "Feature Name": "has_keyboard_seq", "Mathematical Formulation": "I_{kb} \\in \\{0, 1\\}", "Type": "Binary", "Security & ML Purpose": "Detects keyboard spatial trajectories ('qwerty')"},
        {"#": 17, "Feature Name": "has_common_word", "Mathematical Formulation": "I_{dict} \\in \\{0, 1\\}", "Type": "Binary", "Security & ML Purpose": "Detects common dictionary substrings"},
        {"#": 18, "Feature Name": "has_year_pattern", "Mathematical Formulation": "I_{year} \\in \\{0, 1\\}", "Type": "Binary", "Security & ML Purpose": "Detects calendar year suffixes (1900-2039)"},
        {"#": 19, "Feature Name": "pool_size", "Mathematical Formulation": "R \\in \\{10, 26, 36, 52, 62, 95\\}", "Type": "Integer", "Security & ML Purpose": "Effective character alphabet size"},
        {"#": 20, "Feature Name": "entropy_bits", "Mathematical Formulation": "E_{eff} = L \\log_2(R) \\cdot \\eta", "Type": "Float", "Security & ML Purpose": "Estimated brute-force search space complexity"}
    ]
    st.dataframe(pd.DataFrame(feature_table_data), use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("#### 4. Hybrid Synthesis & Cybersecurity Safeguard Arbitration")
    st.write(
        "The final classification is computed by combining continuous heuristic scores with supervised ML class expectations, "
        "governed by deterministic cybersecurity safeguard bounds implemented in `modules/hybrid_engine.py`:"
    )

    st.markdown("**Step A: Normalized Unconstrained Score Fusion:**")
    st.latex(r"S_{\text{rule\_scaled}} = \frac{S_{\text{rule}}}{25.0} \in [0, 4.0]")
    st.latex(r"\mathbb{E}_{\text{ML}}[\text{Class}] = \sum_{c=0}^{4} c \cdot P(\text{Class} = c)")
    st.latex(r"S_{\text{hybrid\_raw}} = \left(w_{\text{rule}} \cdot S_{\text{rule\_scaled}}\right) + \left(w_{\text{ml}} \cdot \mathbb{E}_{\text{ML}}[\text{Class}]\right)")
    st.write("Where the empirical fusion weights are set to $w_{\text{rule}} = 0.45$ and $w_{\text{ml}} = 0.55$.")
    st.latex(r"S_{\text{hybrid}} = 25.0 \cdot S_{\text{hybrid\_raw}} \in [0.0, 100.0]")

    st.markdown("**Step B: Security Weakest-Link Principle & Safeguard Overrides:**")
    st.write("If any vulnerability condition is met, the continuous score is strictly capped:")
    st.latex(r"S_{\text{final}} = \begin{cases} \min(S_{\text{hybrid}}, 18.0) \implies \text{Very Weak} & \text{if Compromised} = \text{True} \\ \min(S_{\text{hybrid}}, S_{\text{rule}} + 6.0, 24.0) \implies \text{Very Weak} & \text{if } S_{\text{rule}} < 25.0 \\ \min(S_{\text{hybrid}}, 38.0) \implies \text{Weak / Very Weak} & \text{if } L < 8 \\ \min(S_{\text{hybrid}}, 38.0) \implies \text{Weak / Very Weak} & \text{if } I_{\text{dict}} = 1 \land L < 12 \\ \min(S_{\text{hybrid}}, 35.0) \implies \text{Weak / Very Weak} & \text{if } I_{\text{kb}} = 1 \land L < 10 \\ S_{\text{hybrid}} & \text{otherwise} \end{cases}")

# -------------------------------------------------------------
# Tab 4: Defense Viva Q&A
# -------------------------------------------------------------
with tab_defense:
    st.subheader("🎓 University External Examiner Viva Defense Q&A")
    st.write("Prepared defense responses for external academic project evaluation:")

    faqs = [
        (
            "Q1. Why combine Rule-based heuristics with Machine Learning rather than using ML alone?",
            "Machine learning models are prone to out-of-distribution adversarial failures (e.g., classifying a long repeated string 'aaaaaaaaaaaaaaaa' as Strong due to high length). Conversely, pure rule-based heuristics cannot capture non-linear morphological relationships. The hybrid architecture combines the probabilistic pattern-matching of ML with deterministic cybersecurity safety bounds that prevent false confidence."
        ),
        (
            "Q2. How is user password privacy protected during Have I Been Pwned API checks?",
            "The system uses SHA-1 k-anonymity. The candidate password is hashed with SHA-1 locally. Only the first 5 hexadecimal characters of the hash (the prefix) are transmitted over TLS to the API. The API returns a list of matching 35-character hash suffixes. The application searches the returned suffixes locally on the client machine. The full hash and plaintext password never leave the user's volatile memory."
        ),
        (
            "Q3. Why was Logistic Regression selected as the Champion model over Decision Trees or Random Forests?",
            "While Random Forests and Decision Trees achieved ~99.8% to 100% accuracy on in-distribution synthetic test splits, their performance dropped sharply on our 250-sample adversarial holdout set. Logistic Regression demonstrated the highest adversarial generalization accuracy (69.6% vs Decision Tree 64.4% and SVM 60.0%), stable class probabilities, and zero risk of deep-tree overfitting."
        ),
        (
            "Q4. What is the justification for overriding ML predictions when a password is found in breaches?",
            "In operational cybersecurity, an exposed password has an effective cracking time of zero seconds because attackers immediately test it via automated credential stuffing. Allowing an ML model to assign a 'Strong' rating to a known breached credential (e.g. 'Summer2024!') would be scientifically invalid and dangerously misleading."
        ),
        (
            "Q5. How does the SQLite audit database ensure privacy compliance?",
            "The database implements a privacy-preserving metadata-only architecture. It records only non-reversible numerical telemetry: evaluation timestamps, composite scores, ML labels, breach risk tiers, entropy bits, and coarse length buckets (<8, 8-11, 12-15, >=16). Plaintext passwords and cryptographic hashes are never written to disk or logs."
        ),
        (
            "Q6. How does this system align with current NIST SP 800-63B standards?",
            "The system implements core NIST SP 800-63B guidelines: validating passwords against breach lists, supporting passphrases up to 64+ characters, avoiding counterproductive arbitrary composition rules, eliminating forced periodic password rotation, and providing a cryptographically secure random passphrase generator."
        )
    ]

    for q, a in faqs:
        st.markdown(f"""
        <div class='viva-box'>
            <div class='viva-q'>{q}</div>
            <div class='viva-a'>{a}</div>
        </div>
        """, unsafe_allow_html=True)
