#!/usr/bin/env python3
"""
Script de correction automatique des tests - Phase 4.1
Corrige les erreurs d'import, fixtures async, et mocks
"""

import os
import re
import subprocess
from pathlib import Path
from typing import List, Tuple

# Couleurs pour l'affichage
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color


def print_step(msg: str):
    print(f"\n{BLUE}[STEP]{NC} {msg}")


def print_success(msg: str):
    print(f"{GREEN}✓{NC} {msg}")


def print_error(msg: str):
    print(f"{RED}✗{NC} {msg}")


def print_warning(msg: str):
    print(f"{YELLOW}⚠{NC} {msg}")


class TestFixer:
    """Classe pour corriger automatiquement les tests"""
    
    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir)
        self.tests_dir = self.base_dir / "tests"
        self.fixes_applied = 0
        self.files_modified = []
        
    def fix_pwd_context_imports(self) -> int:
        """Corrige les imports de pwd_context"""
        print_step("Correction des imports pwd_context...")
        count = 0
        
        for test_file in self.tests_dir.rglob("*.py"):
            content = test_file.read_text()
            original = content
            
            # Remplacer les imports de pwd_context
            content = re.sub(
                r'from app\.core\.security import \((.*?)pwd_context,?(.*?)\)',
                r'from app.core.security import (\1get_password_hash,\2)',
                content,
                flags=re.DOTALL
            )
            
            # Remplacer pwd_context.hash() par get_password_hash()
            content = re.sub(r'pwd_context\.hash\(', 'get_password_hash(', content)
            
            # Remplacer pwd_context.verify() par verify_password()
            content = re.sub(r'pwd_context\.verify\(', 'verify_password(', content)
            
            if content != original:
                test_file.write_text(content)
                count += 1
                self.files_modified.append(str(test_file))
                print_success(f"  Fixed: {test_file.relative_to(self.base_dir)}")
        
        self.fixes_applied += count
        return count
    
    def fix_async_fixtures(self) -> int:
        """Convertit les fixtures sync en async quand nécessaire"""
        print_step("Conversion des fixtures en async...")
        count = 0
        
        for test_file in self.tests_dir.rglob("*.py"):
            content = test_file.read_text()
            original = content
            
            # Ajouter import pytest_asyncio si nécessaire
            if '@pytest.fixture' in content and 'async def' in content:
                if 'import pytest_asyncio' not in content and 'from pytest_asyncio' not in content:
                    # Ajouter l'import après les imports pytest
                    content = re.sub(
                        r'(import pytest\n)',
                        r'\1import pytest_asyncio\n',
                        content
                    )
            
            # Convertir @pytest.fixture en @pytest_asyncio.fixture pour fonctions async
            pattern = r'@pytest\.fixture(\([^)]*\))?\s+async def'
            replacement = r'@pytest_asyncio.fixture\1\nasync def'
            content = re.sub(pattern, replacement, content)
            
            if content != original:
                test_file.write_text(content)
                count += 1
                if str(test_file) not in self.files_modified:
                    self.files_modified.append(str(test_file))
                print_success(f"  Fixed: {test_file.relative_to(self.base_dir)}")
        
        self.fixes_applied += count
        return count
    
    def fix_async_mocks(self) -> int:
        """Remplace MagicMock par AsyncMock pour code async"""
        print_step("Conversion des mocks en async...")
        count = 0
        
        for test_file in self.tests_dir.rglob("*.py"):
            content = test_file.read_text()
            original = content
            
            # Ajouter AsyncMock à l'import si nécessaire
            if 'MagicMock' in content and 'async def test_' in content:
                if 'from unittest.mock import' in content and 'AsyncMock' not in content:
                    content = re.sub(
                        r'from unittest\.mock import ([^)]+)',
                        lambda m: f"from unittest.mock import {m.group(1)}, AsyncMock" if 'AsyncMock' not in m.group(1) else m.group(0),
                        content
                    )
            
            if content != original:
                test_file.write_text(content)
                count += 1
                if str(test_file) not in self.files_modified:
                    self.files_modified.append(str(test_file))
                print_success(f"  Fixed: {test_file.relative_to(self.base_dir)}")
        
        self.fixes_applied += count
        return count
    
    def fix_common_imports(self) -> int:
        """Corrige les imports communs cassés"""
        print_step("Correction des imports communs...")
        count = 0
        
        # Mapping des imports à corriger
        import_fixes = {
            'from app.core.security import pwd_context': 'from app.core.security import get_password_hash, verify_password',
            'from app.db.dependencies import get_db': 'from app.db.dependencies import get_async_db as get_db',
        }
        
        for test_file in self.tests_dir.rglob("*.py"):
            content = test_file.read_text()
            original = content
            
            for old_import, new_import in import_fixes.items():
                if old_import in content:
                    content = content.replace(old_import, new_import)
            
            if content != original:
                test_file.write_text(content)
                count += 1
                if str(test_file) not in self.files_modified:
                    self.files_modified.append(str(test_file))
                print_success(f"  Fixed: {test_file.relative_to(self.base_dir)}")
        
        self.fixes_applied += count
        return count
    
    def run_all_fixes(self) -> Tuple[int, List[str]]:
        """Exécute toutes les corrections"""
        print(f"\n{'='*60}")
        print(f"  Phase 4.1 - Correction automatique des tests")
        print(f"{'='*60}\n")
        
        self.fix_pwd_context_imports()
        self.fix_async_fixtures()
        self.fix_async_mocks()
        self.fix_common_imports()
        
        print(f"\n{'='*60}")
        print(f"{GREEN}✓{NC} Corrections terminées!")
        print(f"  Fichiers modifiés: {len(self.files_modified)}")
        print(f"  Corrections appliquées: {self.fixes_applied}")
        print(f"{'='*60}\n")
        
        return self.fixes_applied, self.files_modified


def run_tests_and_report():
    """Lance les tests et génère un rapport"""
    print_step("Lancement des tests...")
    
    result = subprocess.run(
        ["poetry", "run", "pytest", "tests/", "--tb=no", "-q"],
        capture_output=True,
        text=True,
        cwd="."
    )
    
    output = result.stdout + result.stderr
    
    # Extraire les statistiques
    passed = re.search(r'(\d+) passed', output)
    failed = re.search(r'(\d+) failed', output)
    errors = re.search(r'(\d+) error', output)
    
    print("\n" + "="*60)
    print("  Résultats des tests")
    print("="*60)
    if passed:
        print(f"{GREEN}✓{NC} Tests passés: {passed.group(1)}")
    if failed:
        print(f"{YELLOW}⚠{NC} Tests échoués: {failed.group(1)}")
    if errors:
        print(f"{RED}✗{NC} Erreurs: {errors.group(1)}")
    print("="*60 + "\n")


if __name__ == "__main__":
    fixer = TestFixer()
    fixes, files = fixer.run_all_fixes()
    
    if fixes > 0:
        print_step("Formatage du code avec Black...")
        subprocess.run(["poetry", "run", "black", "tests/", "--line-length", "120", "--quiet"])
        print_success("Code formaté")
        
        run_tests_and_report()
        
        print_step("Fichiers modifiés:")
        for f in files[:10]:  # Afficher les 10 premiers
            print(f"  - {f}")
        if len(files) > 10:
            print(f"  ... et {len(files) - 10} autres fichiers")
    else:
        print_warning("Aucune correction nécessaire")
