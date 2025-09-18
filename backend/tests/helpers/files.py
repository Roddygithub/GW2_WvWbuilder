"""File and I/O test helpers."""
import os
import shutil
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, BinaryIO, Generator, Optional, TextIO, Union

import aiofiles
import aiofiles.os


@contextmanager
def temp_directory() -> Generator[Path, None, None]:
    """Context manager that creates and cleans up a temporary directory.
    
    Yields:
        Path to the temporary directory
    """
    temp_dir = tempfile.mkdtemp()
    try:
        yield Path(temp_dir)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


@contextmanager
def temp_file(
    content: Optional[Union[str, bytes]] = None,
    mode: str = 'w+b',
    suffix: Optional[str] = None,
    prefix: Optional[str] = None,
    dir: Optional[Union[str, Path]] = None,
) -> Generator[Path, None, None]:
    """Context manager that creates and cleans up a temporary file.
    
    Args:
        content: Optional content to write to the file
        mode: File open mode
        suffix: Optional file suffix
        prefix: Optional file prefix
        dir: Optional directory to create the file in
        
    Yields:
        Path to the temporary file
    """
    with tempfile.NamedTemporaryFile(
        mode=mode,
        suffix=suffix or '',
        prefix=prefix or 'test_',
        dir=dir,
        delete=False
    ) as f:
        file_path = Path(f.name)
        if content is not None:
            if 'b' in mode and isinstance(content, str):
                content = content.encode('utf-8')
            f.write(content)
    
    try:
        yield file_path
    finally:
        file_path.unlink(missing_ok=True)


async def create_test_file(
    content: Union[str, bytes],
    directory: Optional[Union[str, Path]] = None,
    filename: Optional[str] = None,
    mode: str = 'w'
) -> Path:
    """Create a test file with the given content.
    
    Args:
        content: File content
        directory: Directory to create the file in (default: system temp dir)
        filename: Optional filename (default: auto-generated)
        mode: File open mode
        
    Returns:
        Path to the created file
    """
    if directory is None:
        directory = Path(tempfile.gettempdir())
    else:
        directory = Path(directory)
    
    if filename is None:
        import uuid
        filename = f"test_{uuid.uuid4().hex}"
    
    file_path = directory / filename
    
    if 'b' in mode and isinstance(content, str):
        content = content.encode('utf-8')
    
    async with aiofiles.open(file_path, mode) as f:
        await f.write(content)
    
    return file_path


async def read_file(file_path: Union[str, Path], mode: str = 'r') -> Union[str, bytes]:
    """Read the contents of a file.
    
    Args:
        file_path: Path to the file
        mode: File open mode ('r' for text, 'rb' for binary)
        
    Returns:
        File content as string or bytes
    """
    async with aiofiles.open(file_path, mode) as f:
        return await f.read()


def assert_file_exists(file_path: Union[str, Path]) -> None:
    """Assert that a file exists.
    
    Args:
        file_path: Path to the file
        
    Raises:
        AssertionError: If the file does not exist
    """
    file_path = Path(file_path)
    assert file_path.exists(), f"File does not exist: {file_path}"
    assert file_path.is_file(), f"Path is not a file: {file_path}"


def assert_file_not_exists(file_path: Union[str, Path]) -> None:
    """Assert that a file does not exist.
    
    Args:
        file_path: Path to the file
        
    Raises:
        AssertionError: If the file exists
    """
    file_path = Path(file_path)
    assert not file_path.exists(), f"File exists but should not: {file_path}"


def assert_file_content(
    file_path: Union[str, Path],
    expected_content: Union[str, bytes],
    encoding: str = 'utf-8'
) -> None:
    """Assert that a file's content matches the expected content.
    
    Args:
        file_path: Path to the file
        expected_content: Expected file content
        encoding: File encoding (for text mode)
        
    Raises:
        AssertionError: If the content does not match
    """
    file_path = Path(file_path)
    assert_file_exists(file_path)
    
    mode = 'rb' if isinstance(expected_content, bytes) else 'r'
    
    with open(file_path, mode, encoding=encoding) as f:
        content = f.read()
    
    assert content == expected_content, f"File content does not match: {file_path}"


class MockFile:
    """Mock file object for testing file uploads and downloads."""
    
    def __init__(
        self,
        content: Union[str, bytes],
        filename: str = "test.txt",
        content_type: str = "text/plain"
    ):
        """Initialize the mock file.
        
        Args:
            content: File content
            filename: Filename
            content_type: Content type
        """
        self.content = content if isinstance(content, bytes) else content.encode('utf-8')
        self.filename = filename
        self.content_type = content_type
    
    def __enter__(self) -> BinaryIO:
        """Enter context manager."""
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w+b')
        self.temp_file.write(self.content)
        self.temp_file.seek(0)
        return self.temp_file
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context manager."""
        if hasattr(self, 'temp_file'):
            self.temp_file.close()
            try:
                os.unlink(self.temp_file.name)
            except OSError:
                pass
    
    def to_upload_file(self) -> tuple:
        """Convert to a tuple for use with FastAPI's UploadFile."""
        return (self.filename, self.content, self.content_type)


class AsyncMockFile:
    """Asynchronous mock file object for testing file uploads and downloads."""
    
    def __init__(
        self,
        content: Union[str, bytes],
        filename: str = "test.txt",
        content_type: str = "text/plain"
    ):
        """Initialize the async mock file.
        
        Args:
            content: File content
            filename: Filename
            content_type: Content type
        """
        self.content = content if isinstance(content, bytes) else content.encode('utf-8')
        self.filename = filename
        self.content_type = content_type
    
    async def __aenter__(self) -> BinaryIO:
        """Enter async context manager."""
        self.temp_file = await aiofiles.tempfile.NamedTemporaryFile(delete=False, mode='w+b')
        await self.temp_file.write(self.content)
        await self.temp_file.seek(0)
        return self.temp_file
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit async context manager."""
        if hasattr(self, 'temp_file'):
            await self.temp_file.close()
            try:
                await aiofiles.os.remove(self.temp_file.name)
            except OSError:
                pass
    
    def to_upload_file(self) -> tuple:
        """Convert to a tuple for use with FastAPI's UploadFile."""
        return (self.filename, self.content, self.content_type)
