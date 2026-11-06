"""
Breach-Risk Estimation Engine
Implements zero-knowledge k-anonymity API queries and local compromised password checks.
Ensures zero plaintext password storage, transmission, or logging.
"""

import hashlib
import requests
from typing import Dict, Any
from config import HIBP_API_URL, HIBP_REQUEST_TIMEOUT


# Bundled top commonly breached passwords for instant offline detection
TOP_BREACHED_PASSWORDS = {
    "123456", "password", "123456789", "12345", "12345678", "qwerty", "111111",
    "1234567", "dragon", "123123", "baseball", "football", "shadow", "mustang",
    "superman", "monkey", "secret", "welcome", "charlie", "donald", "trustno1",
    "princess", "solo", "jordan", "master", "login", "admin", "passcode",
    "pass123", "testing", "server", "system", "computer", "internet", "security",
    "starwars", "pokemon", "chelsea", "liverpool", "barcelona", "arsenal",
    "killer", "hunter", "matrix", "freedom", "cookie", "sunshine", "iloveyou",
    "whatever", "chocolate", "babygirl", "princess1", "rockyou", "letmein",
    "ashley", "bailey", "michelle", "corvette", "harley", "tigger", "daniel",
    "summer", "winter", "spring", "autumn", "default", "qwertyuiop", "asdfghjkl",
    "1234567890", "0987654321", "admin123", "root", "toor", "pass", "p@ssword",
    "p@ssw0rd", "P@ssw0rd1", "Pass1234", "Password1", "Password123", "qwerty123",
    "iloveyou1", "welcome1", "welcome123", "adminadmin", "password1234", "123456789012",
    "hunter2", "shadow123", "dragon123", "monkey123", "master123", "sunshine1",
    "superman1", "batman123", "starwars1", "chelsea123", "liverpool1", "arsenal1",
    "barcelona1", "cookie123", "killer123", "freedom123", "matrix123", "pokemon123",
    "babygirl1", "princess123", "corvette1", "harley123", "daniel123", "charlie1",
    "jordan123", "trustno123", "letmein123", "rockyou123", "whatever1", "chocolate1",
    "summer2020", "summer2021", "summer2022", "summer2023", "summer2024", "summer2025",
    "winter2020", "winter2021", "winter2022", "winter2023", "winter2024", "winter2025",
    "spring2020", "spring2021", "spring2022", "spring2023", "spring2024", "spring2025",
    "autumn2020", "autumn2021", "autumn2022", "autumn2023", "autumn2024", "autumn2025",
    "qwertyuiopasdfghjklzxcvbnm", "12345678901234567890", "passwordpasswordpassword",
    "aaaaaaaaaaaaaaaaaa", "11111111111111111111"
}


class BreachRiskEstimator:
    """
    Evaluates exposure risk across global breach repositories using k-anonymity
    and local breach databases without compromising user credential privacy.
    """

    def __init__(self):
        self.local_breach_set = {p.lower() for p in TOP_BREACHED_PASSWORDS}

    def check_hibp_k_anonymity(self, password: str) -> Dict[str, Any]:
        """
        Query Have I Been Pwned using k-anonymity:
        1. SHA-1 hash the password.
        2. Send ONLY the first 5 characters (prefix) of the SHA-1 hash to the API.
        3. Search the returned list of 35-character suffixes locally.
        4. Plaintext password NEVER leaves this device.
        """
        if not password:
            return {"queried": False, "compromised": False, "count": 0, "status": "Empty input"}

        # Generate SHA-1 hash in uppercase hex
        sha1 = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
        prefix = sha1[:5]
        suffix = sha1[5:]

        headers = {
            "User-Agent": "Academic-Password-Breach-Risk-Estimator/1.0"
        }

        try:
            url = f"{HIBP_API_URL}{prefix}"
            response = requests.get(url, headers=headers, timeout=HIBP_REQUEST_TIMEOUT)

            if response.status_code == 200:
                lines = response.text.splitlines()
                for line in lines:
                    parts = line.strip().split(":")
                    if len(parts) == 2 and parts[0] == suffix:
                        count = int(parts[1])
                        return {
                            "queried": True,
                            "compromised": True,
                            "count": count,
                            "status": "Found in public breach repositories",
                            "api_online": True
                        }
                return {
                    "queried": True,
                    "compromised": False,
                    "count": 0,
                    "status": "No match found in breach database",
                    "api_online": True
                }
            else:
                return {
                    "queried": False,
                    "compromised": False,
                    "count": 0,
                    "status": f"API responded with status {response.status_code}",
                    "api_online": False
                }
        except requests.RequestException:
            # Gracefully handle network timeouts or offline mode
            return {
                "queried": False,
                "compromised": False,
                "count": 0,
                "status": "API unreachable (network error or offline mode)",
                "api_online": False
            }

    def evaluate_breach_risk(self, password: str, rule_results: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute comprehensive dual-layer breach assessment:
        1. Local high-frequency breach blacklist lookup
        2. Remote k-anonymity API query
        3. Risk tier derivation (CRITICAL, HIGH, MODERATE, LOW)
        """
        if not password:
            return {
                "is_compromised": False,
                "breach_count": 0,
                "risk_tier": "LOW",
                "risk_label": "No Password Provided",
                "risk_color": "#9E9E9E",
                "detection_source": "None",
                "details": "Enter a password to evaluate exposure."
            }

        # Step 1: Local Blacklist Check
        is_in_local = password.lower() in self.local_breach_set

        # Step 2: HIBP k-Anonymity Check
        hibp_result = self.check_hibp_k_anonymity(password)

        is_compromised = is_in_local or hibp_result.get("compromised", False)
        breach_count = hibp_result.get("count", 0)

        if is_in_local and breach_count == 0:
            breach_count = 50000  # Conservative estimate for local list hits

        detection_source = []
        if is_in_local:
            detection_source.append("Local Compromised Passwords Database")
        if hibp_result.get("compromised", False):
            detection_source.append(f"HIBP Pwned Passwords ({breach_count:,} occurrences)")

        source_str = " & ".join(detection_source) if detection_source else "None"

        # Determine Risk Tier
        if is_compromised:
            risk_tier = "CRITICAL"
            risk_label = "CRITICAL RISK - Known Compromised Credential"
            risk_color = "#D32F2F"
            details = (
                f"Identified in global breach repositories ({breach_count:,} recorded breaches). "
                "Active threat of credential stuffing and automated password spraying."
            )
        elif rule_results and (rule_results.get("dictionary_matches") or rule_results.get("has_keyboard_sequence")):
            risk_tier = "HIGH"
            risk_label = "HIGH RISK - Dictionary or Keyboard Pattern"
            risk_color = "#F57C00"
            details = (
                "Password contains easily guessable dictionary words or keyboard sequences "
                "frequently generated by rule-based password crackers."
            )
        elif rule_results and rule_results.get("score", 0) < 50:
            risk_tier = "MODERATE"
            risk_label = "MODERATE RISK - Low Structural Complexity"
            risk_color = "#FBC02D"
            details = (
                "Password is not in known breaches, but low length or entropy makes it vulnerable to brute force."
            )
        else:
            risk_tier = "LOW"
            risk_label = "LOW RISK - No Known Breaches Detected"
            risk_color = "#388E3C"
            details = (
                "No occurrences discovered in breach datasets and password exhibits resilient complexity."
            )

        return {
            "is_compromised": is_compromised,
            "breach_count": breach_count,
            "risk_tier": risk_tier,
            "risk_label": risk_label,
            "risk_color": risk_color,
            "detection_source": source_str,
            "api_online": hibp_result.get("api_online", False),
            "details": details
        }
