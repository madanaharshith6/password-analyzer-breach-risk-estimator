"""
History and Audit Log Operations
Functions for recording and retrieving anonymized password analysis statistics.
"""

from typing import List, Dict, Any
from sqlalchemy import func
from database.db import get_session, init_db, PasswordAnalysisRecord


class AuditHistoryManager:
    """
    Manages anonymized historical records of password strength evaluations.
    """

    def __init__(self):
        init_db()

    def record_analysis(
        self,
        strength_category: str,
        rule_score: float,
        ml_prediction: str,
        breach_risk_category: str,
        entropy_score: float,
        password_length: int
    ) -> str:
        """
        Record anonymized audit entry.
        Categorizes length into anonymous buckets (e.g. '<8 chars', '8-11 chars', etc.)
        so exact length is obscured.
        """
        if password_length < 8:
            bucket = "<8 chars"
        elif password_length < 12:
            bucket = "8-11 chars"
        elif password_length < 16:
            bucket = "12-15 chars"
        else:
            bucket = ">=16 chars"

        session = get_session()
        try:
            record = PasswordAnalysisRecord(
                strength_category=strength_category,
                rule_score=float(rule_score),
                ml_prediction=ml_prediction,
                breach_risk_category=breach_risk_category,
                entropy_score=float(entropy_score),
                length_bucket=bucket
            )
            session.add(record)
            session.commit()
            analysis_id = record.analysis_id
            return analysis_id
        finally:
            session.close()

    def get_recent(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve recent anonymized audit records."""
        session = get_session()
        try:
            records = (
                session.query(PasswordAnalysisRecord)
                .order_by(PasswordAnalysisRecord.timestamp.desc())
                .limit(limit)
                .all()
            )
            return [r.to_dict() for r in records]
        finally:
            session.close()

    def get_summary_stats(self) -> Dict[str, Any]:
        """Compute aggregate distributions across audit history."""
        session = get_session()
        try:
            total_count = session.query(PasswordAnalysisRecord).count()
            if total_count == 0:
                return {
                    "total_evaluations": 0,
                    "strength_breakdown": {},
                    "breach_breakdown": {},
                    "avg_rule_score": 0.0,
                    "avg_entropy": 0.0
                }

            # Strength breakdown
            strength_rows = (
                session.query(PasswordAnalysisRecord.strength_category, func.count(PasswordAnalysisRecord.id))
                .group_by(PasswordAnalysisRecord.strength_category)
                .all()
            )
            strength_dist = {cat: count for cat, count in strength_rows}

            # Breach risk breakdown
            breach_rows = (
                session.query(PasswordAnalysisRecord.breach_risk_category, func.count(PasswordAnalysisRecord.id))
                .group_by(PasswordAnalysisRecord.breach_risk_category)
                .all()
            )
            breach_dist = {risk: count for risk, count in breach_rows}

            # Averages
            avg_rule = session.query(func.avg(PasswordAnalysisRecord.rule_score)).scalar() or 0.0
            avg_ent = session.query(func.avg(PasswordAnalysisRecord.entropy_score)).scalar() or 0.0

            return {
                "total_evaluations": total_count,
                "strength_breakdown": strength_dist,
                "breach_breakdown": breach_dist,
                "avg_rule_score": round(float(avg_rule), 1),
                "avg_entropy": round(float(avg_ent), 1)
            }
        finally:
            session.close()

    def clear_all(self) -> int:
        """Purge all historical audit records."""
        session = get_session()
        try:
            count = session.query(PasswordAnalysisRecord).delete()
            session.commit()
            return count
        finally:
            session.close()
