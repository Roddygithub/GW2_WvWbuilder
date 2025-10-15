"""Environment variable test helpers."""

import os
import contextlib
from typing import Any, Dict, Iterator, Optional, Union


@contextlib.contextmanager
def env_vars(
    updates: Dict[str, Optional[Union[str, int, float, bool]]], clear: bool = False
) -> Iterator[None]:
    """Temporarily set environment variables in the test environment.

    Args:
        updates: Dictionary of environment variables to set
        clear: Whether to clear existing environment variables first

    Example:
        >>> with env_vars({"MY_VAR": "test"}):
        ...     assert os.environ["MY_VAR"] == "test"
    """
    old_env = os.environ.copy()

    if clear:
        os.environ.clear()

    # Set new environment variables
    for key, value in updates.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = str(value)

    try:
        yield
    finally:
        # Restore old environment
        os.environ.clear()
        os.environ.update(old_env)


def set_env_var(key: str, value: Optional[Union[str, int, float, bool]]) -> None:
    """Set an environment variable.

    Args:
        key: Environment variable name
        value: Value to set (will be converted to string)
    """
    if value is None:
        os.environ.pop(key, None)
    else:
        os.environ[key] = str(value)


def get_env_var(
    key: str, default: Optional[Union[str, int, float, bool]] = None, type_: type = str
) -> Any:
    """Get an environment variable with type conversion.

    Args:
        key: Environment variable name
        default: Default value if not set
        type_: Type to convert the value to (str, int, float, bool)

    Returns:
        The environment variable value converted to the specified type
    """
    value = os.environ.get(key, None)

    if value is None:
        return default

    if type_ is bool:
        return value.lower() in ("true", "1", "t", "y", "yes")

    try:
        return type_(value)
    except (ValueError, TypeError):
        return default


class MockEnv:
    """Context manager for mocking environment variables."""

    def __init__(
        self,
        updates: Optional[Dict[str, Optional[Union[str, int, float, bool]]]] = None,
        clear: bool = False,
    ):
        """Initialize the mock environment.

        Args:
            updates: Dictionary of environment variables to set
            clear: Whether to clear existing environment variables first
        """
        self.updates = updates or {}
        self.clear = clear
        self._old_env = None

    def __enter__(self) -> "MockEnv":
        """Enter the context manager."""
        self._old_env = os.environ.copy()

        if self.clear:
            os.environ.clear()

        for key, value in self.updates.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = str(value)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the context manager."""
        if self._old_env is not None:
            os.environ.clear()
            os.environ.update(self._old_env)

    def set(self, key: str, value: Optional[Union[str, int, float, bool]]) -> None:
        """Set an environment variable.

        Args:
            key: Environment variable name
            value: Value to set
        """
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = str(value)

    def get(self, key: str, default: Optional[Any] = None, type_: type = str) -> Any:
        """Get an environment variable with type conversion.

        Args:
            key: Environment variable name
            default: Default value if not set
            type_: Type to convert the value to (str, int, float, bool)

        Returns:
            The environment variable value converted to the specified type
        """
        return get_env_var(key, default=default, type_=type_)


@contextlib.contextmanager
def disable_env_vars(*vars_to_remove: str) -> Iterator[None]:
    """Temporarily remove environment variables.

    Args:
        *vars_to_remove: Names of environment variables to remove

    Example:
        >>> with disable_env_vars("MY_VAR", "ANOTHER_VAR"):
        ...     assert "MY_VAR" not in os.environ
    """
    old_values = {}

    for var in vars_to_remove:
        old_values[var] = os.environ.pop(var, None)

    try:
        yield
    finally:
        for var, value in old_values.items():
            if value is not None:
                os.environ[var] = value
