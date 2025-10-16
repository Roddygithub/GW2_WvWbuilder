#!/usr/bin/env python3
"""Fix missing imports causing MyPy 'Name not defined' errors."""

import re
from pathlib import Path
from typing import Dict, Set


# Map of undefined names to their import statements
IMPORT_FIXES = {
    'team_members': 'from app.models.association_tables import team_members',
    'selectinload': 'from sqlalchemy.orm import selectinload',
    'User': 'from app.models.user import User',
    'Profession': 'from app.models.profession import Profession',
    'Webhook': 'from app.models.webhook import Webhook',
    'uuid': 'import uuid',
    'timezone': 'from datetime import timezone',
}


def fix_imports_in_file(file_path: Path) -> int:
    """Add missing imports to a file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    imports_to_add: Set[str] = set()
    
    # Check which imports are needed
    for name, import_stmt in IMPORT_FIXES.items():
        # Check if name is used but not imported
        if name in content and import_stmt not in content:
            # Verify it's actually undefined (not in a string, comment, etc.)
            pattern = rf'\b{re.escape(name)}\b'
            if re.search(pattern, content):
                imports_to_add.add(import_stmt)
    
    if not imports_to_add:
        return 0
    
    # Find where to insert imports (after existing imports)
    insert_index = 0
    in_imports = False
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Track if we're in import section
        if stripped.startswith(('import ', 'from ')):
            in_imports = True
            insert_index = i + 1
        elif in_imports and stripped and not stripped.startswith('#'):
            # End of import section
            break
    
    # Insert new imports
    for import_stmt in sorted(imports_to_add):
        lines.insert(insert_index, import_stmt)
        insert_index += 1
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    return len(imports_to_add)


def main():
    """Process all Python files."""
    app_dir = Path(__file__).parent.parent / 'app'
    
    total_fixed = 0
    files_modified = 0
    
    for py_file in app_dir.rglob('*.py'):
        if '__pycache__' in str(py_file):
            continue
        
        try:
            fixed = fix_imports_in_file(py_file)
            if fixed > 0:
                print(f"Added {fixed} imports to {py_file.relative_to(app_dir.parent)}")
                total_fixed += fixed
                files_modified += 1
        except Exception as e:
            print(f"Error processing {py_file}: {e}")
    
    print(f"\nTotal: {total_fixed} imports added to {files_modified} files")
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
