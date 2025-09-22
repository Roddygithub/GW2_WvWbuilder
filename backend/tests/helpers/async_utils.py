"""Asynchronous test utilities."""

import asyncio
import inspect
from functools import wraps
from typing import Any, Awaitable, Callable, Optional, Type, TypeVar

from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


def async_test(
    func: Optional[Callable[..., Awaitable[Any]]] = None,
    timeout: Optional[float] = 10.0,
    loop_factory: Optional[Callable[[], asyncio.AbstractEventLoop]] = None,
) -> Callable:
    """Decorator for async test functions.

    Args:
        func: The async test function to decorate
        timeout: Maximum time in seconds to wait for the test to complete
        loop_factory: Optional event loop factory

    Returns:
        A synchronous test function that runs the async test
    """

    def decorator(test_func: Callable[..., Awaitable[Any]]) -> Callable:
        @wraps(test_func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            loop = (loop_factory or asyncio.new_event_loop)()
            return loop.run_until_complete(
                asyncio.wait_for(test_func(*args, **kwargs), timeout=timeout, loop=loop)
            )

        return wrapper

    if func is not None:
        return decorator(func)
    return decorator


async def wait_for(
    condition: Callable[..., Awaitable[bool]],
    timeout: float = 5.0,
    interval: float = 0.1,
    **kwargs: Any,
) -> bool:
    """Wait for a condition to become true.

    Args:
        condition: Async callable that returns a boolean
        timeout: Maximum time to wait in seconds
        interval: Time between condition checks
        **kwargs: Additional arguments to pass to the condition

    Returns:
        True if the condition became true, False if the timeout was reached
    """
    elapsed = 0.0
    while elapsed < timeout:
        if await condition(**kwargs):
            return True
        await asyncio.sleep(interval)
        elapsed += interval
    return False


class AsyncClientFactory:
    """Factory for creating test API clients."""

    def __init__(self, app: FastAPI, base_url: str = "http://test"):
        """Initialize the client factory.

        Args:
            app: FastAPI application
            base_url: Base URL for the test client
        """
        self.app = app
        self.base_url = base_url

    async def __aenter__(self) -> AsyncClient:
        """Enter async context manager."""
        self.client = AsyncClient(app=self.app, base_url=self.base_url)
        await self.client.__aenter__()
        return self.client

    async def __aexit__(self, *args: Any, **kwargs: Any) -> None:
        """Exit async context manager."""
        await self.client.__aexit__(*args, **kwargs)


async def assert_async_raises(
    exception_type: Type[Exception],
    func: Callable[..., Awaitable[Any]],
    *args: Any,
    **kwargs: Any,
) -> Exception:
    """Assert that an async function raises an exception.

    Args:
        exception_type: Expected exception type
        func: Async function to call
        *args: Positional arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function

    Returns:
        The raised exception

    Raises:
        AssertionError: If the expected exception is not raised
    """
    try:
        await func(*args, **kwargs)
    except exception_type as e:
        return e
    except Exception as e:
        raise AssertionError(
            f"Expected {exception_type.__name__}, but got {type(e).__name__}: {e}"
        ) from e
    else:
        raise AssertionError(f"Expected {exception_type.__name__} was not raised")


async def gather_with_concurrency(
    n: int, *tasks: Awaitable[T], return_exceptions: bool = False
) -> list[T]:
    """Run coroutines with limited concurrency.

    Args:
        n: Maximum number of concurrent tasks
        *tasks: Coroutines to run
        return_exceptions: Whether to return exceptions as results

    Returns:
        List of results in the same order as the input tasks
    """
    semaphore = asyncio.Semaphore(n)

    async def sem_task(task: Awaitable[T]) -> T:
        async with semaphore:
            return await task

    return await asyncio.gather(
        *(sem_task(task) for task in tasks), return_exceptions=return_exceptions
    )


async def run_in_threadpool(func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    """Run a synchronous function in a thread pool.

    Args:
        func: Function to run
        *args: Positional arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function

    Returns:
        The result of the function call
    """
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda: func(*args, **kwargs))


async def create_test_session(
    app: FastAPI, **override_dependencies: Any
) -> AsyncSession:
    """Create a test database session with overridden dependencies.

    Args:
        app: FastAPI application
        **override_dependencies: Dependencies to override

    Returns:
        A new database session
    """
    from app.db.session import AsyncSessionLocal

    # Create a new session with overridden dependencies
    async with AsyncSessionLocal() as session:
        for dep_name, dep_value in override_dependencies.items():
            app.dependency_overrides[dep_name] = dep_value

        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            # Clean up overridden dependencies
            for dep_name in override_dependencies:
                app.dependency_overrides.pop(dep_name, None)

            await session.close()


def async_to_sync(func: Callable[..., Awaitable[T]]) -> Callable[..., T]:
    """Convert an async function to a synchronous one.

    Args:
        func: Async function to convert

    Returns:
        Synchronous wrapper function
    """
    if not inspect.iscoroutinefunction(func):
        return func  # type: ignore

    @wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> T:
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(func(*args, **kwargs))
        finally:
            loop.close()

    return sync_wrapper


def sync_to_async(func: Callable[..., T]) -> Callable[..., Awaitable[T]]:
    """Convert a synchronous function to an async one.

    Args:
        func: Synchronous function to convert

    Returns:
        Async wrapper function
    """
    if inspect.iscoroutinefunction(func):
        return func  # type: ignore

    @wraps(func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> T:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, lambda: func(*args, **kwargs))

    return async_wrapper
