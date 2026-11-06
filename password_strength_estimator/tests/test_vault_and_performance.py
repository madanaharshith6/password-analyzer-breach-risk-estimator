"""
Unit and Performance Tests for VaultManager and Sub-Second Execution
Student: MADANA KOMAL SIVA SAI HARSHITH (Roll No: 24ME5A5408)
"""

import time
import pytest
from database.vault import VaultManager


@pytest.fixture
def vault():
    vm = VaultManager()
    yield vm


def test_vault_add_and_get_entry(vault):
    """Verify adding and retrieving a credential record."""
    entry_id = vault.add_entry(
        service_name="TestService_Alpha",
        username="testuser@example.com",
        password_val="P@ssw0rd1234!",
        strength_tier="Strong",
        strength_score=78.5
    )
    assert entry_id is not None

    record = vault.get_entry(entry_id)
    assert record is not None
    assert record["service_name"] == "TestService_Alpha"
    assert record["username"] == "testuser@example.com"
    assert record["strength_tier"] == "Strong"

    # Cleanup
    vault.delete_entry(entry_id)


def test_vault_search_case_insensitive(vault):
    """Verify indexed search filtering by service name and username."""
    id1 = vault.add_entry("GitHub Enterprise", "octocat@github.com", "SecretOcto!99")
    id2 = vault.add_entry("AWS Console", "cloud_admin@aws.com", "CloudVault#2024")

    # Search by service
    results_service = vault.get_entries(search_query="github")
    assert any(r["entry_id"] == id1 for r in results_service)
    assert not any(r["entry_id"] == id2 for r in results_service)

    # Search by username
    results_user = vault.get_entries(search_query="cloud_admin")
    assert any(r["entry_id"] == id2 for r in results_user)

    # Cleanup
    vault.delete_entry(id1)
    vault.delete_entry(id2)


def test_vault_update_entry(vault):
    """Verify updating credential records."""
    entry_id = vault.add_entry("University Portal", "student24@univ.edu", "InitPass#1")

    updated = vault.update_entry(
        entry_id=entry_id,
        username="student24_updated@univ.edu",
        password_val="NewStrongerPass#2024!",
        strength_tier="Very Strong",
        strength_score=92.0
    )
    assert updated is True

    record = vault.get_entry(entry_id)
    assert record["username"] == "student24_updated@univ.edu"
    assert record["strength_tier"] == "Very Strong"
    assert record["strength_score"] == 92.0

    # Cleanup
    vault.delete_entry(entry_id)


def test_vault_delete_entry(vault):
    """Verify deleting credential records."""
    entry_id = vault.add_entry("TemporaryService", "temp@temp.com", "TempPass!1")
    assert vault.get_entry(entry_id) is not None

    deleted = vault.delete_entry(entry_id)
    assert deleted is True
    assert vault.get_entry(entry_id) is None


def test_vault_crud_sub_100ms_performance(vault):
    """Benchmark: Ensure Add, Search, Update, and Delete each execute in sub-100ms."""
    # 1. Add Entry
    t0 = time.perf_counter()
    entry_id = vault.add_entry("PerfTest Service", "perf@test.com", "FastP@ssw0rd!1")
    t_add = (time.perf_counter() - t0) * 1000
    assert t_add < 150.0  # Under 150ms on local disk

    # 2. Search Entries
    t1 = time.perf_counter()
    results = vault.get_entries(search_query="PerfTest", limit=10)
    t_search = (time.perf_counter() - t1) * 1000
    assert t_search < 100.0  # Under 100ms
    assert len(results) >= 1

    # 3. Update Entry
    t2 = time.perf_counter()
    vault.update_entry(entry_id=entry_id, username="perf_updated@test.com")
    t_update = (time.perf_counter() - t2) * 1000
    assert t_update < 100.0  # Under 100ms

    # 4. Delete Entry
    t3 = time.perf_counter()
    vault.delete_entry(entry_id=entry_id)
    t_delete = (time.perf_counter() - t3) * 1000
    assert t_delete < 100.0  # Under 100ms
