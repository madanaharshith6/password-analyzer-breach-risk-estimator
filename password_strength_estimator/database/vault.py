"""
Password Vault & Credential Manager Operations
Optimized CRUD with sub-millisecond execution, transactions, and privacy safeguards.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy import or_, desc
from database.db import get_session, init_db, VaultCredential


class VaultManager:
    """
    High-performance, local privacy-preserving password credential manager.
    Supports indexed case-insensitive search, paginated views, updates, and deletes.
    """

    def __init__(self):
        init_db()

    def add_entry(
        self,
        service_name: str,
        username: str,
        password_val: str,
        strength_tier: str = "Moderate",
        strength_score: float = 50.0
    ) -> str:
        """Add a new credential entry to the vault with transaction commit."""
        session = get_session()
        try:
            record = VaultCredential(
                service_name=service_name.strip(),
                username=username.strip(),
                password_val=password_val,
                strength_tier=strength_tier,
                strength_score=float(strength_score)
            )
            session.add(record)
            session.commit()
            return record.entry_id
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_entries(
        self,
        search_query: str = "",
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Retrieve paginated credential entries with optional search filtering."""
        session = get_session()
        try:
            query = session.query(VaultCredential)
            if search_query.strip():
                pattern = f"%{search_query.strip().lower()}%"
                query = query.filter(
                    or_(
                        VaultCredential.service_name.ilike(pattern),
                        VaultCredential.username.ilike(pattern)
                    )
                )
            records = query.order_by(desc(VaultCredential.updated_at)).offset(offset).limit(limit).all()
            return [r.to_dict() for r in records]
        finally:
            session.close()

    def count_entries(self, search_query: str = "") -> int:
        """Count total matching entries for fast pagination calculation."""
        session = get_session()
        try:
            query = session.query(VaultCredential)
            if search_query.strip():
                pattern = f"%{search_query.strip().lower()}%"
                query = query.filter(
                    or_(
                        VaultCredential.service_name.ilike(pattern),
                        VaultCredential.username.ilike(pattern)
                    )
                )
            return query.count()
        finally:
            session.close()

    def get_entry(self, entry_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a single credential entry by entry_id."""
        session = get_session()
        try:
            record = session.query(VaultCredential).filter_by(entry_id=entry_id).first()
            return record.to_dict() if record else None
        finally:
            session.close()

    def update_entry(
        self,
        entry_id: str,
        service_name: Optional[str] = None,
        username: Optional[str] = None,
        password_val: Optional[str] = None,
        strength_tier: Optional[str] = None,
        strength_score: Optional[float] = None
    ) -> bool:
        """Update an existing credential entry."""
        session = get_session()
        try:
            record = session.query(VaultCredential).filter_by(entry_id=entry_id).first()
            if not record:
                return False

            if service_name is not None:
                record.service_name = service_name.strip()
            if username is not None:
                record.username = username.strip()
            if password_val is not None:
                record.password_val = password_val
            if strength_tier is not None:
                record.strength_tier = strength_tier
            if strength_score is not None:
                record.strength_score = float(strength_score)

            session.commit()
            return True
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def delete_entry(self, entry_id: str) -> bool:
        """Delete an entry from the vault."""
        session = get_session()
        try:
            record = session.query(VaultCredential).filter_by(entry_id=entry_id).first()
            if not record:
                return False
            session.delete(record)
            session.commit()
            return True
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def clear_all(self) -> int:
        """Purge all stored credentials from the vault."""
        session = get_session()
        try:
            count = session.query(VaultCredential).delete()
            session.commit()
            return count
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
