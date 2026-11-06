"""
Page 3: Security Insights & Password Vulnerability Analytics
Deep-Dive into Attacker Heuristics, Brute-Force Combinatorics, and NIST SP 800-63B Standards
Student: MADANA KOMAL SIVA SAI HARSHITH (Roll No: 24ME5A5408)
"""

import sys
import math
import secrets
from pathlib import Path
import streamlit as st
import pandas as pd

# Setup paths
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

st.set_page_config(page_title="Security Insights • Hybrid Estimator", page_icon="💡", layout="wide")

st.markdown("""
<style>
    .page-title {
        font-size: 2rem;
        font-weight: 800;
        color: #38bdf8;
        margin-bottom: 0.2rem;
    }
    .insight-card {
        background-color: #131d31;
        border: 1px solid #1e293b;
        border-radius: 8px;
        padding: 1.1rem;
        margin-bottom: 0.9rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    .card-title {
        font-size: 0.98rem;
        font-weight: 700;
        margin-bottom: 0.4rem;
    }
    .card-desc {
        font-size: 0.84rem;
        color: #cbd5e1;
        line-height: 1.45;
    }
    .nist-req {
        border-left: 3px solid #38bdf8;
    }
    .nist-rec {
        border-left: 3px solid #4ade80;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='page-title'>💡 Password Security Insights & Attack Modeling</div>", unsafe_allow_html=True)
st.caption("Mathematical foundations of search-space entropy, GPU cracking speeds, NIST SP 800-63B guidelines, and secure passphrase generation.")

# -------------------------------------------------------------
# Crack Time Formatter Utility (Fixes 0.0 Million Years Rounding Bug)
# -------------------------------------------------------------
def format_crack_duration(seconds: float) -> str:
    """
    Format time into intuitive, monotonically increasing units.
    Prevents aggressive rounding that causes non-zero values to display as '0.0 million years'.
    """
    if seconds < 1e-4:
        return "< 0.1 millisecond"
    elif seconds < 1e-2:
        return f"{seconds * 1000:.1f} milliseconds"
    elif seconds < 1.0:
        return f"{seconds * 1000:.0f} milliseconds"
    elif seconds < 60:
        return f"{seconds:.2f} seconds"
    elif seconds < 3600:
        return f"{seconds / 60:.1f} minutes"
    elif seconds < 86400:
        return f"{seconds / 3600:.1f} hours"
    elif seconds < 31536000:
        return f"{seconds / 86400:.1f} days"
    elif seconds < 31536000 * 1000:
        yrs = seconds / 31536000
        return f"{yrs:.1f} years"
    elif seconds < 31536000 * 1e6:
        k_yrs = seconds / (31536000 * 1e3)
        return f"{k_yrs:.1f} thousand years"
    elif seconds < 31536000 * 1e9:
        m_yrs = seconds / (31536000 * 1e6)
        return f"{m_yrs:.2f} million years"
    elif seconds < 31536000 * 1e12:
        b_yrs = seconds / (31536000 * 1e9)
        return f"{b_yrs:.2f} billion years"
    else:
        t_yrs = seconds / (31536000 * 1e12)
        return f"{t_yrs:.2e} trillion years"


# Tabbed Layout
tab_sim, tab_patterns, tab_nist, tab_generator = st.tabs([
    "🧮 Brute-Force Entropy Simulator",
    "⚠️ Attack Vectors & Pattern Analysis",
    "📜 NIST SP 800-63B Guidelines",
    "🎲 Passphrase Generator"
])

# -------------------------------------------------------------
# Tab 1: Interactive Combinatorics & Entropy Simulator
# -------------------------------------------------------------
with tab_sim:
    st.subheader("🧮 Interactive Brute-Force Search Space & Crack Time Calculator")
    st.write(
        "Modern password recovery attacks are massively parallelized across specialized GPU clusters (e.g., Hashcat on RTX 4090 rigs). "
        "Adjust the parameters below to explore theoretical combinatorial complexity under ideal, uniformly random conditions."
    )

    c_sim1, c_sim2 = st.columns([1.1, 1.3])

    with c_sim1:
        sim_len = st.slider("Password Length ($L$ in characters):", min_value=4, max_value=24, value=10)
        use_lower = st.checkbox("Include Lowercase Characters (a-z, 26)", value=True)
        use_upper = st.checkbox("Include Uppercase Characters (A-Z, 26)", value=True)
        use_digits = st.checkbox("Include Numeric Digits (0-9, 10)", value=True)
        use_specials = st.checkbox("Include Special Symbols (33 printable symbols)", value=False)

        pool = 0
        if use_lower: pool += 26
        if use_upper: pool += 26
        if use_digits: pool += 10
        if use_specials: pool += 33
        pool = max(pool, 1)

        total_combinations = pool ** sim_len
        entropy_bits = sim_len * math.log2(pool)

        st.markdown(f"""
        <div class='insight-card'>
            <div><b>Active Character Pool Size ($R$):</b> <code>{pool} characters</code></div>
            <div><b>Password Length ($L$):</b> <code>{sim_len} characters</code></div>
            <div><b>Total Search Space ($N = R^L$):</b> <code>{total_combinations:.2e} combinations</code></div>
            <div><b>Theoretical Shannon Entropy ($E = L \\log_2 R$):</b> <code>{entropy_bits:.2f} bits</code></div>
        </div>
        """, unsafe_allow_html=True)

        st.caption(
            "⚠️ **Crucial Modeling Assumption:** This calculation assumes characters are chosen independently "
            "and uniformly at random. Real human-selected passwords exhibit heavy structural bias, dictionary roots, "
            "and spatial keyboard runs, meaning attackers can crack them in a tiny fraction of theoretical brute-force time."
        )

    with c_sim2:
        st.markdown("<div style='font-size:0.95rem; font-weight:700; color:#e2e8f0; margin-bottom:0.4rem;'>Estimated Search Time by Attacker Capability Profile</div>", unsafe_allow_html=True)
        attacker_speeds = [
            ("Standard Laptop CPU", 1e7, "10 Million guesses/s"),
            ("Single Modern GPU (1x RTX 4090)", 1e10, "10 Billion guesses/s"),
            ("Enterprise Cracking Rig (8x RTX 4090)", 1e11, "100 Billion guesses/s"),
            ("Nation-State GPU Cluster", 1e12, "1 Trillion guesses/s")
        ]

        crack_table = []
        for profile, rate, rate_label in attacker_speeds:
            worst_case_sec = total_combinations / rate
            avg_case_sec = worst_case_sec / 2.0  # Average time to locate secret is 50% of keyspace

            crack_table.append({
                "Attacker Profile": profile,
                "Hash Rate": rate_label,
                "Average Crack Time (50% Keyspace)": format_crack_duration(avg_case_sec),
                "Worst-Case Crack Time (100% Keyspace)": format_crack_duration(worst_case_sec)
            })

        st.dataframe(pd.DataFrame(crack_table), use_container_width=True, hide_index=True)

# -------------------------------------------------------------
# Tab 2: Attack Vectors & Patterns
# -------------------------------------------------------------
with tab_patterns:
    st.subheader("⚠️ Common Password Attack Vectors & Adversarial Patterns")
    st.write(
        "Attackers rarely execute exhaustive brute-force cracking on high-entropy spaces. "
        "Instead, they deploy targeted probabilistic techniques that exploit human cognitive predictability."
    )

    c_pat1, c_pat2 = st.columns(2)

    with c_pat1:
        st.markdown("""
        <div class='insight-card'>
            <div class='card-title' style='color:#ef4444;'>1. Rule-Based Mutation Attacks (e.g., Hashcat best64)</div>
            <div class='card-desc'>
                Attackers feed known dictionary words through deterministic transformation rules:
                <ul>
                    <li>Capitalizing first or last character (<code>password</code> &rarr; <code>Password</code>)</li>
                    <li>Leetspeak substitutions (<code>o</code> &rarr; <code>0</code>, <code>e</code> &rarr; <code>3</code>, <code>a</code> &rarr; <code>@</code>)</li>
                    <li>Appending current years and symbols (<code>Summer</code> &rarr; <code>Summer2024!</code>)</li>
                </ul>
                <b>Academic Insight:</b> Substituting <code>@</code> for <code>a</code> provides negligible security because crackers evaluate these patterns first.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class='insight-card'>
            <div class='card-title' style='color:#f97316;'>2. Spatial Keyboard Walk Trajectories</div>
            <div class='card-desc'>
                When prompted to input complex passwords, users routinely trace physical keyboard geometry:
                <code>qwerty</code>, <code>asdfgh</code>, <code>1qaz2wsx</code>, <code>zxcvbnm</code>.
                Modern cracking frameworks utilize dedicated dictionaries covering spatial keyboard walks across QWERTY, AZERTY, and QWERTZ layouts.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class='insight-card'>
            <div class='card-title' style='color:#eab308;'>3. Repetitive Runs & Monotonous Strings</div>
            <div class='card-desc'>
                Strings with high length but minimal unique characters (e.g. <code>aaaaaaaaaaaaaaaa</code> or <code>123123123123</code>)
                confuse naive entropy calculators. Our hybrid engine applies a strict repetition penalty to prevent artificial score inflation.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c_pat2:
        st.markdown("""
        <div class='insight-card'>
            <div class='card-title' style='color:#38bdf8;'>4. Credential Stuffing & Public Dumps</div>
            <div class='card-desc'>
                Billions of compromised credential pairs from historic breaches (RockYou, Collection #1-5, LinkedIn, Adobe) 
                circulate in public forums. Automated botnets replay these exact combinations against unrelated web targets.
                <br><br>
                <b>Critical Technical Distinction:</b>
                Offline brute-force crack time reflects the computational cost of inverting a hash. 
                In credential stuffing, <b>attack time is effectively zero seconds</b> because the plaintext is already published.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class='insight-card'>
            <div class='card-title' style='color:#a855f7;'>5. Predictable Calendar Year & Date Suffixes</div>
            <div class='card-desc'>
                A substantial fraction of corporate passwords append the active calendar year (e.g., <code>Company2023!</code> &rarr; <code>Company2024!</code>).
                Our feature extraction module incorporates a dedicated regex feature ($I_{\\text{year}}$) to penalize this exact predictable pattern.
            </div>
        </div>
        """, unsafe_allow_html=True)

# -------------------------------------------------------------
# Tab 3: NIST SP 800-63B Guidelines
# -------------------------------------------------------------
with tab_nist:
    st.subheader("📜 Modern Password Standards: NIST Special Publication 800-63B")
    st.write(
        "The National Institute of Standards and Technology (NIST) overhauled authentication guidelines in **SP 800-63B** "
        "(Digital Identity Guidelines: Authentication and Lifecycle Management) to eliminate obsolete, counterproductive policies."
    )

    nist_data = [
        {
            "Security Domain": "Minimum Password Length",
            "NIST SP 800-63B Guidance": "Requirement: Minimum 8 characters for user-chosen passwords (16+ recommended for system-generated).",
            "Classification": "Requirement",
            "Security Rationale": "Shorter lengths cannot withstand modern GPU cluster parallelism."
        },
        {
            "Security Domain": "Maximum Password Length",
            "NIST SP 800-63B Guidance": "Requirement: Support at least 64 characters; accept all printable ASCII and Unicode characters.",
            "Classification": "Requirement",
            "Security Rationale": "Enables users to select long, memorable multi-word passphrases with whitespace."
        },
        {
            "Security Domain": "Arbitrary Composition Rules",
            "NIST SP 800-63B Guidance": "Do NOT require arbitrary complexity rules (e.g. mandatory upper, lower, digit, symbol mix).",
            "Classification": "Guideline / Abolished Practice",
            "Security Rationale": "Composition rules do not increase entropy; users adopt predictable habits (e.g. initial cap, trailing '!1')."
        },
        {
            "Security Domain": "Periodic Password Expiration",
            "NIST SP 800-63B Guidance": "Do NOT require periodic rotation (e.g., mandatory 60 or 90-day resets) without evidence of compromise.",
            "Classification": "Guideline / Abolished Practice",
            "Security Rationale": "Forced expiration leads to predictable incremental modifications (e.g., Spring2023 to Summer2023)."
        },
        {
            "Security Domain": "Compromised-Credential Screening",
            "NIST SP 800-63B Guidance": "Requirement: Screen candidate passwords against known breach lists, dictionary words, and repetitive strings.",
            "Classification": "Requirement",
            "Security Rationale": "Prevents users from employing credentials actively weaponized in credential-stuffing attacks."
        },
        {
            "Security Domain": "Knowledge-Based Questions",
            "NIST SP 800-63B Guidance": "Do NOT use knowledge-based authentication ('mother's maiden name') or password hints.",
            "Classification": "Prohibited Practice",
            "Security Rationale": "Answers to personal security questions are readily discoverable via OSINT and social engineering."
        },
        {
            "Security Domain": "Password Managers",
            "NIST SP 800-63B Guidance": "Permit paste functionality and encourage integration with reputable password managers.",
            "Classification": "Recommendation",
            "Security Rationale": "Facilitates adoption of cryptographically random, high-entropy unique credentials."
        }
    ]

    st.dataframe(pd.DataFrame(nist_data), use_container_width=True, hide_index=True)

    st.markdown(
        "🔗 **Official Reference:** View the complete NIST publication at "
        "[NIST Special Publication 800-63B (Section 5.1.1.2)](https://pages.nist.gov/800-63-3/sp800-63b.html)."
    )

# -------------------------------------------------------------
# Tab 4: Cryptographically Secure Passphrase Generator
# -------------------------------------------------------------
with tab_generator:
    st.subheader("🎲 Cryptographically Secure Multi-Word Passphrase Generator")
    st.write(
        "Multi-word passphrases offer superior combinatorial search-space entropy while remaining straightforward to memorize. "
        "This generator utilizes Python's **`secrets` module** (cryptographically strong pseudo-random number generator) "
        "to ensure uncorrelated word and token selections."
    )

    # Curated authentic 256-word cryptographic dictionary
    PASSPHRASE_WORDLIST = [
        "acorn", "albatross", "alchemy", "alder", "amber", "anchor", "anthem", "apex",
        "apricot", "aquifer", "arcade", "arch", "archive", "arrow", "asteroid", "atlas",
        "aurora", "avalanche", "axiom", "badge", "badger", "banner", "baron", "basalt",
        "beacon", "beaver", "bison", "blizzard", "boulder", "bramble", "breeze", "bridge",
        "bronze", "canyon", "castle", "catalyst", "cedar", "chalet", "channel", "circuit",
        "citadel", "clover", "cobalt", "comet", "compass", "condor", "copper", "coral",
        "crag", "crane", "crater", "crescent", "crest", "crystal", "cypress", "dagger",
        "delta", "desert", "dynamo", "eagle", "echo", "eclipse", "elm", "ember",
        "emerald", "enclave", "falcon", "fathom", "feather", "fern", "fjord", "flint",
        "forest", "forge", "fossil", "fox", "frost", "galaxy", "garnet", "geyser",
        "glacier", "glade", "granite", "grove", "gulf", "harbor", "hawk", "hazard",
        "heather", "helix", "horizon", "iceberg", "indigo", "inlet", "iron", "island",
        "jaguar", "javelin", "juniper", "kelp", "lagoon", "lantern", "lark", "latitude",
        "ledger", "lichen", "limestone", "lynx", "magnet", "maple", "marble", "matrix",
        "meadow", "meteor", "minnow", "mirage", "monolith", "moon", "moss", "mountain",
        "nebula", "nest", "neutron", "nexus", "nickel", "nimbus", "nitrogen", "nomad",
        "nova", "oasis", "obsidian", "ocean", "onyx", "orbit", "osprey", "otter",
        "outpost", "palisade", "panther", "peak", "pebble", "pelican", "pennant", "perimeter",
        "phoenix", "pinnacle", "pine", "pioneer", "plateau", "plover", "polar", "ponderosa",
        "poplar", "prairie", "prism", "pulsar", "pyramid", "quarry", "quartz", "quasar",
        "radius", "rapids", "raven", "reef", "resonance", "ridge", "rift", "river",
        "rooster", "sable", "saffron", "sage", "sapphire", "saturn", "savanna", "scarlet",
        "schooner", "scout", "sequoia", "shadow", "shale", "shoal", "silver", "sierra",
        "solitude", "sonar", "sparrow", "spear", "spectrum", "spire", "spring", "spruce",
        "stalwart", "starling", "steppe", "stone", "stratum", "summit", "swallow", "swift",
        "talisman", "tamarack", "tempest", "terminal", "terrace", "thistle", "thunder", "timber",
        "titan", "topaz", "torrent", "totem", "trail", "trench", "tundra", "twilight",
        "typhoon", "valley", "vanguard", "vector", "velocity", "vernal", "vessel", "vortex",
        "voyage", "walrus", "waterfall", "wave", "whisper", "willow", "wind", "wolf",
        "wolverine", "woodland", "zenith", "zephyr", "abacus", "bamboo", "calico", "driftwood",
        "espresso", "flute", "guitar", "harpoon", "iguana", "jamboree", "kayak", "mango",
        "nugget", "origami", "papyrus", "quiver", "radish", "tulip", "umbrella", "violin"
    ]

    col_gen1, col_gen2 = st.columns([1.1, 1.3])

    with col_gen1:
        num_words = st.slider("Number of Random Words ($k$):", min_value=3, max_value=6, value=4)
        separator = st.selectbox("Word Separator:", options=["-", "_", ".", " "], index=0)
        include_digit = st.checkbox("Append Random 2-Digit Number (00-99)", value=True)
        include_symbol = st.checkbox("Append Random Special Symbol (!@#$%^&*)", value=True)

        c_btn1, c_btn2 = st.columns(2)
        with c_btn1:
            gen_btn = st.button("🎲 Generate", type="primary", use_container_width=True)
        with c_btn2:
            regen_btn = st.button("🔄 Regenerate", type="secondary", use_container_width=True)

    with col_gen2:
        # Cryptographically secure random choice using secrets module
        wordlist_size = len(PASSPHRASE_WORDLIST)
        word_entropy_per_unit = math.log2(wordlist_size)  # log2(256) = 8.0 bits

        if gen_btn or regen_btn or "passphrase_val" not in st.session_state:
            selected_words = [secrets.choice(PASSPHRASE_WORDLIST) for _ in range(num_words)]
            assembled_phrase = separator.join([w.capitalize() for w in selected_words])

            added_entropy = 0.0
            if include_digit:
                rand_num = secrets.randbelow(100)  # 00 to 99 (100 possibilities)
                assembled_phrase += f"{rand_num:02d}"
                added_entropy += math.log2(100)  # ~6.64 bits

            if include_symbol:
                symbol_pool = "!@#$%^&*"
                chosen_sym = secrets.choice(symbol_pool)
                assembled_phrase += chosen_sym
                added_entropy += math.log2(len(symbol_pool))  # 3.0 bits

            total_gen_entropy = (num_words * word_entropy_per_unit) + added_entropy

            st.session_state["passphrase_val"] = assembled_phrase
            st.session_state["passphrase_entropy"] = total_gen_entropy
            st.session_state["passphrase_len"] = len(assembled_phrase)

        passphrase_current = st.session_state.get("passphrase_val", "")
        entropy_current = st.session_state.get("passphrase_entropy", 0.0)

        st.markdown("<div style='font-size:0.85rem; font-weight:600; color:#94a3b8;'>GENERATED SECURE PASSPHRASE</div>", unsafe_allow_html=True)
        st.code(passphrase_current, language=None)

        st.markdown(f"""
        <div style='background:#131d31; border:1px solid #1e293b; border-radius:6px; padding:0.75rem 0.9rem; font-size:0.82rem; color:#94a3b8;'>
            • <b>Wordlist Size:</b> {wordlist_size} distinct words ({word_entropy_per_unit:.1f} bits/word)<br>
            • <b>Total Length:</b> {len(passphrase_current)} characters<br>
            • <b>Exact Generation Entropy:</b> <code>{entropy_current:.2f} bits</code><br>
            • <b>Theoretical Search Space:</b> <code>2^{entropy_current:.1f} ({2**entropy_current:.2e})</code> combinations
        </div>
        """, unsafe_allow_html=True)
        st.caption("Privacy guarantee: Generated credentials are processed strictly in volatile memory and never persisted.")
