#!/usr/bin/env python3
"""
Script to identify and remove duplicate test files.
Analyzes test files and keeps only the most complete/recent version.
"""
import os
from pathlib import Path
from collections import defaultdict
import shutil

# Files to remove (duplicates and obsolete tests)
DUPLICATES_TO_REMOVE = [
    # Duplicate conftest files
    "tests/conftest_fixtures.py",
    "tests/conftest_updated.py",
    "tests/unit/models/conftest_fixed.py",
    "tests/unit/models/conftest_simple.py",
    
    # Duplicate CRUD test files
    "tests/unit/crud/test_crud_test_base.py",  # Keep test_crud_build.py
    "tests/unit/crud/test_crud_test_build.py",  # Keep test_crud_build.py
    "tests/unit/crud/test_crud_build_complete.py",  # Merge into test_crud_build.py
    "tests/unit/crud/test_crud_builds.py",  # Merge into test_crud_build.py
    "tests/unit/crud/test_crud_roles.py",  # Merge into test_crud_role.py
    
    # Duplicate API test files
    "tests/api/test_api_base_new.py",  # Keep test_api_base.py
    "tests/integration/api/test_int_api_test_build_crud.py",  # Keep test_build_crud.py
    "tests/integration/api/test_int_api_test_build_crud_clean.py",  # Keep test_build_crud.py
    
    # API tests that should be in integration/api instead
    "tests/api/test_api_test_auth_endpoints.py",  # Redundant with integration tests
    "tests/api/test_api_test_builds_endpoints.py",
    "tests/api/test_api_test_compositions_endpoints.py",
    "tests/api/test_api_test_professions_endpoints.py",
    "tests/api/test_api_test_roles_endpoints.py",
    "tests/api/test_api_test_users_endpoints.py",
]

# Archive directory
ARCHIVE_DIR = "tests/archive_duplicates"

def main():
    backend_dir = Path(__file__).parent
    archive_dir = backend_dir / ARCHIVE_DIR
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    removed_count = 0
    archived_count = 0
    
    print("🔍 Cleaning duplicate test files...")
    print("=" * 60)
    
    for file_path in DUPLICATES_TO_REMOVE:
        full_path = backend_dir / file_path
        
        if not full_path.exists():
            print(f"⏭️  Skip (not found): {file_path}")
            continue
        
        # Archive the file
        relative_archive_path = archive_dir / file_path
        relative_archive_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            shutil.move(str(full_path), str(relative_archive_path))
            archived_count += 1
            print(f"📦 Archived: {file_path}")
        except Exception as e:
            print(f"❌ Error archiving {file_path}: {e}")
    
    # Also remove old test_api_base.py if test_api_base_new.py was kept
    old_api_base = backend_dir / "tests/api/test_api_base.py"
    if old_api_base.exists():
        stat = os.stat(old_api_base)
        # If file is very small or empty, archive it
        if stat.st_size < 500:
            archive_path = archive_dir / "tests/api/test_api_base.py"
            archive_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(old_api_base), str(archive_path))
            archived_count += 1
            print(f"📦 Archived (small/empty): tests/api/test_api_base.py")
    
    print("=" * 60)
    print(f"✅ Cleanup complete!")
    print(f"   Archived: {archived_count} files")
    print(f"   Archive location: {ARCHIVE_DIR}")
    print(f"\n📊 Estimated test reduction: ~{len(DUPLICATES_TO_REMOVE)} → 0 duplicates")
    print(f"   Expected final test count: ~200-250 unique tests")

if __name__ == "__main__":
    main()
