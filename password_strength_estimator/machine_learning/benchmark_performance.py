"""
Performance Benchmarking Suite for Password Manager & Navigation Latency
Student: MADANA KOMAL SIVA SAI HARSHITH (Roll No: 24ME5A5408)
"""

import sys
import time
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from database.vault import VaultManager


def run_benchmarks():
    results = {}

    # 1. Measure Initial Application Startup / Config Import
    t0 = time.perf_counter()
    import config
    results["initial_app_startup_ms"] = round((time.perf_counter() - t0) * 1000, 2)

    # 2. Measure Clicking / Importing Password Manager Module (Navigation)
    t1 = time.perf_counter()
    import database.vault
    results["navigation_click_response_ms"] = round((time.perf_counter() - t1) * 1000, 2)

    # 3. Measure Rendering the Password Manager Page (Simulated UI Render)
    t2 = time.perf_counter()
    vm = VaultManager()
    total_count = vm.count_entries()
    records = vm.get_entries(limit=10)
    results["render_page_initial_ms"] = round((time.perf_counter() - t2) * 1000, 2)

    # 4. Measure Loading Saved Records (50 items)
    t3 = time.perf_counter()
    loaded = vm.get_entries(limit=50)
    results["loading_saved_records_ms"] = round((time.perf_counter() - t3) * 1000, 2)

    # 5. Measure Adding a New Entry
    t4 = time.perf_counter()
    entry_id = vm.add_entry(
        service_name="BenchmarkService",
        username="bench_user@example.com",
        password_val="S3cur3#Bench2024!",
        strength_tier="Strong",
        strength_score=85.0
    )
    results["add_new_entry_ms"] = round((time.perf_counter() - t4) * 1000, 2)

    # 6. Measure Searching Records (Indexed query)
    t5 = time.perf_counter()
    search_hits = vm.get_entries(search_query="Bench", limit=10)
    results["search_records_ms"] = round((time.perf_counter() - t5) * 1000, 2)

    # 7. Measure Updating an Entry
    t6 = time.perf_counter()
    vm.update_entry(entry_id, username="bench_updated@example.com", strength_score=88.0)
    results["update_entry_ms"] = round((time.perf_counter() - t6) * 1000, 2)

    # 8. Measure Deleting an Entry
    t7 = time.perf_counter()
    vm.delete_entry(entry_id)
    results["delete_entry_ms"] = round((time.perf_counter() - t7) * 1000, 2)

    out_file = BASE_DIR / "machine_learning" / "saved_model" / "performance_benchmarks.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=4)

    print("Performance Benchmarks Summary (Measured):")
    for k, v in results.items():
        print(f"  - {k}: {v} ms")

    return results


if __name__ == "__main__":
    run_benchmarks()
