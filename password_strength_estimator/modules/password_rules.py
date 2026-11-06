"""
Password Rule-Based Evaluation Engine
Evaluates password structural characteristics, patterns, entropy, and vulnerabilities.
"""

import math
import re
from typing import Dict, Any, List
from config import COMMON_DICTIONARY_WORDS, KEYBOARD_PATTERNS


class PasswordRuleEngine:
    """
    Comprehensive rule-based evaluator assessing password complexity,
    entropy, sequential runs, keyboard patterns, and dictionary vulnerabilities.
    """

    def __init__(self):
        self.common_words = set(COMMON_DICTIONARY_WORDS)
        self.keyboard_patterns = [p.lower() for p in KEYBOARD_PATTERNS]

    def calculate_shannon_entropy(self, password: str) -> float:
        """Calculate Shannon entropy in bits per character."""
        if not password:
            return 0.0
        length = len(password)
        frequency = {}
        for char in password:
            frequency[char] = frequency.get(char, 0) + 1
        entropy = 0.0
        for count in frequency.values():
            p = count / length
            entropy -= p * math.log2(p)
        return round(entropy, 3)

    def calculate_pool_size(self, password: str) -> int:
        """Estimate the character space / pool size based on character classes present."""
        pool = 0
        if any(c.islower() for c in password):
            pool += 26
        if any(c.isupper() for c in password):
            pool += 26
        if any(c.isdigit() for c in password):
            pool += 10
        if any(not c.isalnum() for c in password):
            pool += 33
        return max(pool, 1)

    def calculate_entropy_bits(self, password: str) -> float:
        """
        Calculate realistic brute-force search space entropy.
        Penalizes low-variety or monotonous passwords where combinatorial independence is violated.
        """
        if not password:
            return 0.0
        pool = self.calculate_pool_size(password)
        shannon = self.calculate_shannon_entropy(password)
        unique_count = len(set(password))

        # If password contains only 1 or 2 unique characters, search space is minimal
        if unique_count <= 2:
            return round(math.log2(pool), 2)

        max_shannon = math.log2(pool) if pool > 1 else 1.0
        efficiency = min(1.0, max(0.1, shannon / max_shannon))
        theoretical = len(password) * math.log2(pool)
        return round(theoretical * efficiency, 2)

    def find_max_consecutive_repeated(self, password: str) -> int:
        """Find the maximum consecutive identical character run length."""
        if not password:
            return 0
        max_run = 1
        current_run = 1
        for i in range(1, len(password)):
            if password[i] == password[i - 1]:
                current_run += 1
                max_run = max(max_run, current_run)
            else:
                current_run = 1
        return max_run

    def check_alphabetical_sequence(self, password: str, min_length: int = 3) -> bool:
        """Check for sequential alphabetical patterns like 'abc', 'xyz', 'cba'."""
        lower = password.lower()
        if len(lower) < min_length:
            return False
        for i in range(len(lower) - min_length + 1):
            sub = lower[i:i + min_length]
            if all(c.isalpha() for c in sub):
                diffs = [ord(sub[j+1]) - ord(sub[j]) for j in range(len(sub) - 1)]
                if all(d == 1 for d in diffs) or all(d == -1 for d in diffs):
                    return True
        return False

    def check_numerical_sequence(self, password: str, min_length: int = 3) -> bool:
        """Check for sequential numeric patterns like '123', '321', '789'."""
        if len(password) < min_length:
            return False
        for i in range(len(password) - min_length + 1):
            sub = password[i:i + min_length]
            if sub.isdigit():
                diffs = [ord(sub[j+1]) - ord(sub[j]) for j in range(len(sub) - 1)]
                if all(d == 1 for d in diffs) or all(d == -1 for d in diffs):
                    return True
        return False

    def check_keyboard_sequences(self, password: str, min_length: int = 4) -> bool:
        """Detect contiguous keyboard layout walks (e.g. 'qwer', 'asdf', '1234')."""
        lower = password.lower()
        if len(lower) < min_length:
            return False
        for row in self.keyboard_patterns:
            rev_row = row[::-1]
            for i in range(len(lower) - min_length + 1):
                sub = lower[i:i + min_length]
                if sub in row or sub in rev_row:
                    return True
        return False

    def check_dictionary_words(self, password: str) -> List[str]:
        """Detect dictionary words or common password roots."""
        lower = password.lower()
        matches = []
        for word in self.common_words:
            if word in lower and len(word) >= 4:
                matches.append(word)
        return matches

    def check_year_pattern(self, password: str) -> bool:
        """Detect common 4-digit year patterns (1900-2035)."""
        match = re.search(r"(19\d\d|20[0-3]\d)", password)
        return bool(match)

    def estimate_crack_time(self, entropy_bits: float) -> str:
        """
        Estimate crack time assuming an offline brute-force attacker
        capable of 100 billion (10^11) guesses per second (modern GPU cluster).
        """
        if entropy_bits <= 0:
            return "Instantaneous"
        combinations = 2 ** min(entropy_bits, 128)
        seconds = combinations / (1e11)

        if seconds < 0.001:
            return "Instantaneous (< 1 millisecond)"
        elif seconds < 1:
            return f"{round(seconds * 1000, 1)} milliseconds"
        elif seconds < 60:
            return f"{round(seconds, 1)} seconds"
        elif seconds < 3600:
            return f"{round(seconds / 60, 1)} minutes"
        elif seconds < 86400:
            return f"{round(seconds / 3600, 1)} hours"
        elif seconds < 31536000:
            return f"{round(seconds / 86400, 1)} days"
        elif seconds < 31536000 * 1000:
            return f"{round(seconds / 31536000, 1)} years"
        elif seconds < 31536000 * 1e6:
            return f"{round(seconds / (31536000 * 1000), 1)} thousand years"
        elif seconds < 31536000 * 1e9:
            return f"{round(seconds / (31536000 * 1e6), 1)} million years"
        else:
            return "Centuries (Computationally infeasible)"

    def evaluate(self, password: str) -> Dict[str, Any]:
        """
        Execute full rule-based analysis on the supplied password.
        Returns score (0-100), strength category, detailed checklist, and deductions.
        """
        if not password:
            return {
                "score": 0.0,
                "category": "Very Weak",
                "length": 0,
                "entropy_per_char": 0.0,
                "total_entropy_bits": 0.0,
                "pool_size": 1,
                "crack_time": "Instantaneous",
                "rules_passed": [],
                "rules_failed": ["Password is empty"],
                "penalties": ["No password provided"],
                "details": {}
            }

        length = len(password)
        num_upper = sum(1 for c in password if c.isupper())
        num_lower = sum(1 for c in password if c.islower())
        num_digits = sum(1 for c in password if c.isdigit())
        num_special = sum(1 for c in password if not c.isalnum())
        unique_chars = len(set(password))

        shannon_ent = self.calculate_shannon_entropy(password)
        entropy_bits = self.calculate_entropy_bits(password)
        pool_size = self.calculate_pool_size(password)
        crack_time = self.estimate_crack_time(entropy_bits)

        max_repeats = self.find_max_consecutive_repeated(password)
        has_alpha_seq = self.check_alphabetical_sequence(password)
        has_num_seq = self.check_numerical_sequence(password)
        has_kb_seq = self.check_keyboard_sequences(password)
        dict_matches = self.check_dictionary_words(password)
        has_year = self.check_year_pattern(password)

        # Baseline Scoring System (out of 100)
        score = 0.0
        rules_passed = []
        rules_failed = []
        penalties = []

        # 1. Length Scoring (up to 35 points)
        if length >= 16:
            score += 35
            rules_passed.append("Excellent length (>= 16 characters) [+35]")
        elif length >= 12:
            score += 28
            rules_passed.append("Strong length (12-15 characters) [+28]")
        elif length >= 8:
            score += 18
            rules_passed.append("Acceptable minimum length (8-11 characters) [+18]")
        else:
            score += max(0, length * 2)
            rules_failed.append(f"Inadequate length ({length} characters; minimum 8 recommended)")

        # 2. Character Diversity (up to 30 points)
        variety_count = sum([num_lower > 0, num_upper > 0, num_digits > 0, num_special > 0])
        if variety_count == 4:
            score += 30
            rules_passed.append("Complete character diversity (Upper, Lower, Numbers, Symbols) [+30]")
        elif variety_count == 3:
            score += 20
            rules_passed.append("Good character diversity (3 distinct character types) [+20]")
        elif variety_count == 2:
            score += 10
            rules_passed.append("Partial character diversity (2 character types) [+10]")
        else:
            score += 2
            rules_failed.append("Single character type only (High predictability)")

        # Specific type bonuses
        if num_special >= 2:
            score += 5
            rules_passed.append("Multiple special characters present [+5]")
        if num_digits >= 2 and num_upper >= 2:
            score += 5
            rules_passed.append("Balanced combination of numbers and uppercase [+5]")

        # 3. Shannon Entropy Bonus (up to 15 points)
        if shannon_ent >= 3.3:
            score += 15
            rules_passed.append(f"High information density ({shannon_ent:.2f} bits/char) [+15]")
        elif shannon_ent >= 2.6:
            score += 10
            rules_passed.append(f"Moderate information density ({shannon_ent:.2f} bits/char) [+10]")
        elif shannon_ent >= 1.8:
            score += 5
        else:
            rules_failed.append(f"Very low Shannon entropy ({shannon_ent:.2f} bits/char)")

        # 4. Total Search Space Entropy Bonus (up to 15 points)
        if entropy_bits >= 75:
            score += 15
            rules_passed.append(f"Extensive brute-force search space ({entropy_bits:.1f} bits) [+15]")
        elif entropy_bits >= 50:
            score += 10
            rules_passed.append(f"Adequate search space ({entropy_bits:.1f} bits) [+10]")
        elif entropy_bits >= 35:
            score += 5

        # Deductions / Penalties
        if max_repeats >= 3:
            deduction = min(20, (max_repeats - 1) * 6)
            score -= deduction
            penalties.append(f"Consecutive repeated characters (max run: {max_repeats}) [-{deduction}]")
            rules_failed.append(f"Contains {max_repeats} repeated characters in a row")

        if has_alpha_seq:
            score -= 12
            penalties.append("Sequential alphabetical sequence detected (e.g., 'abc') [-12]")
            rules_failed.append("Alphabetical sequence found")

        if has_num_seq:
            score -= 12
            penalties.append("Sequential numerical sequence detected (e.g., '123') [-12]")
            rules_failed.append("Numerical sequence found")

        if has_kb_seq:
            score -= 15
            penalties.append("Keyboard walk pattern detected (e.g., 'qwerty', 'asdf') [-15]")
            rules_failed.append("Keyboard sequence pattern found")

        if dict_matches:
            deduction = min(30, len(dict_matches) * 15)
            score -= deduction
            penalties.append(f"Dictionary roots/common words found ({', '.join(dict_matches)}) [-{deduction}]")
            rules_failed.append(f"Contains common word pattern: {', '.join(dict_matches)}")

        if has_year:
            score -= 8
            penalties.append("Predictable 4-digit calendar year detected [-8]")
            rules_failed.append("Calendar year pattern found")

        # Hard length cap: Passwords below 8 characters can never exceed Weak (< 40)
        if length < 8:
            score = min(score, 25.0 + max(0, length * 1.5))

        # Hard repetition cap: Trivial monotonic repeats (e.g., 'aaaaaaaaaaaaaaaaaa')
        if unique_chars <= 2 or shannon_ent < 1.0:
            score = min(score, 14.0)
            penalties.append("Negligible entropy: extreme character repetition")
            rules_failed.append("Near-zero information density")

        # Hard sequence cap: Long numbers or keyboard walks
        if (has_num_seq and variety_count == 1) or (has_kb_seq and variety_count <= 2):
            score = min(score, 22.0)
            penalties.append("Monotonous sequence/keyboard walk pattern limits security")
            rules_failed.append("Trivial sequence vulnerability")

        # Hard dictionary repetition cap: (e.g., 'passwordpasswordpassword')
        if dict_matches and (unique_chars / max(1, length)) < 0.45:
            score = min(score, 22.0)
            penalties.append("Repeated dictionary root pattern")
            rules_failed.append("Low unique character ratio with dictionary root")

        # Clamp score between 0 and 100
        final_score = max(0.0, min(100.0, round(score, 1)))

        # Categorize into 5 standard tiers
        if final_score < 25.0:
            category = "Very Weak"
        elif final_score < 45.0:
            category = "Weak"
        elif final_score < 65.0:
            category = "Moderate"
        elif final_score < 85.0:
            category = "Strong"
        else:
            category = "Very Strong"

        return {
            "score": final_score,
            "category": category,
            "length": length,
            "uppercase_count": num_upper,
            "lowercase_count": num_lower,
            "digits_count": num_digits,
            "special_count": num_special,
            "variety_count": variety_count,
            "unique_chars": unique_chars,
            "shannon_entropy": shannon_ent,
            "total_entropy_bits": entropy_bits,
            "pool_size": pool_size,
            "crack_time": crack_time,
            "max_consecutive_repeated": max_repeats,
            "has_alphabetical_sequence": has_alpha_seq,
            "has_numerical_sequence": has_num_seq,
            "has_keyboard_sequence": has_kb_seq,
            "dictionary_matches": dict_matches,
            "has_year_pattern": has_year,
            "rules_passed": rules_passed,
            "rules_failed": rules_failed,
            "penalties": penalties
        }
