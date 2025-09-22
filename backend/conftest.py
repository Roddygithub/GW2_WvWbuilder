"""Pytest configuration and fixtures."""
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set environment variable to indicate test environment
os.environ["TESTING"] = "1"

# Import test fixtures
from tests.conftest import *  # noqa: F403, F401
