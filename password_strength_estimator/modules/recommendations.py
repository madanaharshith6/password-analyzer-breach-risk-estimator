"""
Actionable Security Recommendation Engine
Generates prioritized, contextual security advice based on evaluated password weaknesses.
"""

from typing import Dict, Any, List


class RecommendationEngine:
    """
    Produces actionable, NIST 800-63B compliant recommendations to guide
    users toward creating resilient, unguessable credentials.
    """

    def generate(self, rule_results: Dict[str, Any], breach_results: Dict[str, Any] = None) -> List[Dict[str, str]]:
        """
        Produce prioritized list of recommendations.
        Each recommendation has:
        - 'priority': 'HIGH', 'MEDIUM', 'INFO', or 'CRITICAL'
        - 'title': concise summary
        - 'description': detailed guidance
        """
        recs = []

        # 1. Critical: Known Breach or Compromise
        if breach_results and breach_results.get("is_compromised", False):
            count = breach_results.get("breach_count", 0)
            recs.append({
                "priority": "CRITICAL",
                "title": "Compromised in Known Data Breaches",
                "description": (
                    f"This exact password has appeared {count:,} times in publicly known credential dumps. "
                    "Attackers use automated credential stuffing lists containing this password. "
                    "Never use this password under any circumstances."
                )
            })

        # 2. Critical: Extreme Short Length
        length = rule_results.get("length", 0)
        if length == 0:
            recs.append({
                "priority": "CRITICAL",
                "title": "Password is Empty",
                "description": "Please enter a non-empty password for strength and vulnerability analysis."
            })
            return recs

        if length < 8:
            recs.append({
                "priority": "CRITICAL",
                "title": "Length Below Minimum Safety Threshold",
                "description": (
                    f"At only {length} characters, this password can be cracked in seconds via modern GPU brute force. "
                    "Increase length to at least 12-16 characters."
                )
            })
        elif length < 12:
            recs.append({
                "priority": "MEDIUM",
                "title": "Increase Length Beyond 12 Characters",
                "description": (
                    "Passwords between 8 and 11 characters are vulnerable to fast hash-cracking rigs. "
                    "Aim for 14+ characters or a multi-word passphrase for exponential keyspace expansion."
                )
            })

        # 3. High: Common Dictionary Words
        dict_words = rule_results.get("dictionary_matches", [])
        if dict_words:
            recs.append({
                "priority": "HIGH",
                "title": f"Remove Dictionary Substrings ({', '.join(dict_words)})",
                "description": (
                    "Dictionary words are the very first patterns tested by cracking engines like Hashcat and John the Ripper. "
                    "Replace common words with randomized character sequences or uncorrelated passphrases."
                )
            })

        # 4. High: Keyboard Sequences
        if rule_results.get("has_keyboard_sequence", False):
            recs.append({
                "priority": "HIGH",
                "title": "Eliminate Keyboard Walking Sequences",
                "description": (
                    "Patterns like 'qwerty', 'asdf', or '1234' represent spatial keyboard walks easily mapped "
                    "by Markov-chain and rule-based attack heuristics."
                )
            })

        # 5. Medium: Sequential Patterns
        if rule_results.get("has_alphabetical_sequence", False) or rule_results.get("has_numerical_sequence", False):
            recs.append({
                "priority": "MEDIUM",
                "title": "Break Sequential Runs",
                "description": (
                    "Sequential runs like 'abc' or '123' substantially degrade combinatorial entropy. "
                    "Use random character distributions rather than predictable increments."
                )
            })

        # 6. Medium: Repeated Characters
        max_repeats = rule_results.get("max_consecutive_repeated", 1)
        if max_repeats >= 3:
            recs.append({
                "priority": "MEDIUM",
                "title": "Avoid Repeated Characters",
                "description": (
                    f"A run of {max_repeats} identical characters reduces information density. "
                    "Diversify characters rather than repeating the same symbol."
                )
            })

        # 7. Medium: Calendar Year Pattern
        if rule_results.get("has_year_pattern", False):
            recs.append({
                "priority": "MEDIUM",
                "title": "Avoid Appending Calendar Years",
                "description": (
                    "Appending 4-digit years (e.g. 1995, 2024) is one of the most common user habits targeted "
                    "by automated dictionary mutation rules."
                )
            })

        # 8. Character Diversity Missing
        missing = []
        if rule_results.get("uppercase_count", 0) == 0:
            missing.append("uppercase letters (A-Z)")
        if rule_results.get("lowercase_count", 0) == 0:
            missing.append("lowercase letters (a-z)")
        if rule_results.get("digits_count", 0) == 0:
            missing.append("numbers (0-9)")
        if rule_results.get("special_count", 0) == 0:
            missing.append("special symbols (!@#$...)")

        if missing:
            recs.append({
                "priority": "MEDIUM",
                "title": "Expand Character Pool",
                "description": f"Include missing character categories: {', '.join(missing)} to maximize combinatorial search space."
            })

        # 9. General Passphrase Best Practice
        if len(recs) <= 1 and length >= 14:
            recs.append({
                "priority": "INFO",
                "title": "Strong Password Structure Detected",
                "description": (
                    "This password exhibits high entropy and strong complexity metrics. "
                    "Ensure you store it in a reputable password manager and enable Multi-Factor Authentication (MFA)."
                )
            })

        return recs
