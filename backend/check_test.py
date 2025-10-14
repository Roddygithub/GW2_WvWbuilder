import ast
import sys

def check_syntax(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        ast.parse(content)
        print(f"No syntax errors found in {file_path}")
        return True
    except SyntaxError as e:
        print(f"Syntax error in {file_path} at line {e.lineno}, column {e.offset}: {e.msg}")
        print(f"Line {e.lineno}: {e.text}")
        return False
    except Exception as e:
        print(f"Error checking {file_path}: {str(e)}")
        return False

if __name__ == "__main__":
    test_file = "tests/unit/api/test_deps_enhanced.py"
    if not check_syntax(test_file):
        sys.exit(1)
