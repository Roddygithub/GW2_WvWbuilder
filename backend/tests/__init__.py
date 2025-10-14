"""Test package for the GW2 WvW Builder application.

This package contains all test modules and test utilities for the application.
It provides a comprehensive testing framework including unit tests, integration tests,
and various test helpers and fixtures.
"""

# Import test configuration and fixtures
from . import conftest  # noqa: F401

# Import test helpers
try:
    from .helpers import (  # noqa: F401
        random_string,
        random_email,
        random_password,
    )
except ImportError:
    pass

# Import test data factories
try:
    from .helpers.factories import (  # noqa: F401
        create_user,
        create_role,
        create_permission,
        create_profession,
        create_build,
        create_composition,
    )
except ImportError:
    # Si les factories ne sont pas disponibles, on continue sans elles
    pass
